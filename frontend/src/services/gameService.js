import { reactive } from 'vue'
import Game, { Player } from '../models/game.js'
import * as events from '../constants/events.js'
const API_URL = import.meta.env.VITE_API_URL;

const state = reactive({
  ws: null,
  connected: false,
  game: new Game(),
  player: new Player(),
  phaseQuestions: [],
  currentPhaseQuestionIndex: 0,
  currentQuestionAnswersCount: 0,
  _seenAnswerIds: [],
  guesses: {},
  // counts per question: { [questionId]: [ { playerId, name, count } ] }
  guessCounts: {}
})
state.currentGameQuestionText = null

// currently selected game_question id for phases that reference specific game questions (phase 2)
state.currentGameQuestionId = null

// Persisted session (for reconnect)
const STORAGE_KEY = 'furor.session'
function saveSession({ gameCode, playerName, role }) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ gameCode, playerName, role }))
}
function loadSession() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null') } catch { return null }
}
function clearSession() { localStorage.removeItem(STORAGE_KEY) }

let reconnectTimer = null
let reconnectAttempts = 0

function connect(gameId, playerName, router, role = 'player') {
  if (state.ws) {
    console.warn("Ya existe una conexión WebSocket activa.")
    return
  }

  // Convert API_URL (http://...) to WebSocket URL (ws://...)
  const wsUrl = (API_URL || 'http://localhost:8000').replace(/^http/, 'ws')
  const ws = new WebSocket(`${wsUrl}/ws/${gameId}`)
  state.ws = ws

  ws.onopen = () => {
    state.connected = true
    reconnectAttempts = 0
    console.log(`✅ Conectado al WebSocket (partida ${gameId})`)
    state.player = new Player(0,playerName)
    saveSession({ gameCode: gameId, playerName, role })

    ws.send(JSON.stringify({
      action: events.PLAYER_EVENTS.JOIN_GAME,
      player: playerName
    }))

    // pide snapshot por si reingresa a mitad de partida
    requestSync()
  }

  ws.onmessage = handleMessage(router)

  ws.onerror = (error) => {
    console.error("❌ Error WebSocket:", error)
    console.error("URL intentada:", `${wsUrl}/ws/${gameId}`)
  }

  ws.onclose = (event) => {
    console.log("🔌 WebSocket cerrado", event.code, event.reason)
    state.connected = false
    state.ws = null
    //scheduleReconnect(router)
  }
}

function handleMessage(router) {
  return (event) => {
    const msg = JSON.parse(event.data)
    console.log("Mensaje recibido:", msg)

    switch (msg.type) {
      case events.SERVER_EVENTS.PLAYER_JOINED:
        handle_PLAYER_JOINED(msg)
        break
      case events.SERVER_EVENTS.GAME_UPDATED:
        handle_GAME_UPDATED(msg)
        break
      case events.SERVER_EVENTS.PHASE_CHANGED:
        handle_PHASE_CHANGED(msg, router)
        break
      case events.SERVER_EVENTS.QUESTION_CHANGED:
        handle_QUESTION_CHANGED(msg)
        break
      case events.SERVER_EVENTS.PLAYER_LEFT:
        handle_PLAYER_LEFT(msg)
        break
      case events.SERVER_EVENTS.NEW_ANSWER:
        handle_NEW_ANSWER(msg)
        break
      case events.SERVER_EVENTS.GUESS_UPDATED:
        handle_GUESS_UPDATED(msg)
        break
      default:
        console.warn("Tipo de mensaje desconocido:", msg.type)
        return
    }
  }
}

function scheduleReconnect(router) {
  const session = loadSession();
  if (!session) return;

  const delay = Math.min(30000, 1000 * Math.pow(2, reconnectAttempts++)); // exponential backoff
  clearTimeout(reconnectTimer);
  reconnectTimer = setTimeout(() => {
    console.log(`🔁 Reintentando reconexión (intento ${reconnectAttempts})...`);
    connect(session.gameCode, session.playerName, router, session.role);
  }, delay);
}

// Llamar en el bootstrap de la app (p.ej., en main.js) para restaurar sesión
function initFromStorage(router) {
  const session = loadSession()
  if (!session) return
  if (!state.connected && !state.ws) {
    connect(session.gameCode, session.playerName, router, session.role)
  }
}

function requestSync() {
  send(events.PLAYER_EVENTS.REQUEST_UPDATE, {})
}

function send(action, payload = {}) {
  if (!state.ws || state.ws.readyState !== WebSocket.OPEN) return
  state.ws.send(JSON.stringify({ action, ...payload }))
}

function disconnect() {
  if (state.ws) {
    state.ws.close()
    state.ws = null
    state.connected = false
  }
}

// HANDLERS ***************************************************************************************************
function handle_NEW_ANSWER(msg) {
  console.log("NEW_ANSWER RECEIVED:", msg.data.answer)

  // Si el backend envía un id de respuesta, evitar duplicados
  const ans = msg.data?.answer || {}
  const ansId = ans.id
  if (ansId != null) {
    if (!state._seenAnswerIds.includes(ansId)) {
      state._seenAnswerIds.push(ansId)
      state.currentQuestionAnswersCount = state._seenAnswerIds.length
    } else {
      // duplicate, ignorar
      console.debug('Respuesta duplicada recibida, ignorando', ansId)
    }
  } else if (typeof msg.data?.total_answers === 'number') {
    // Si el backend manda total_answers, usarlo
    state.currentQuestionAnswersCount = msg.data.total_answers
  } else {
    // Fallback: incrementar a la llegada de cada NEW_ANSWER
    state.currentQuestionAnswersCount = (state.currentQuestionAnswersCount || 0) + 1
  }

  // Fase 2: contar por canción (original_answer_id) cuántas veces cada jugador fue seleccionado
  try {
    const phase = state.game?.phase
    console.log("Current game phase in handle_NEW_ANSWER:", phase)
    if (String(phase) === '2') {
      const qid = ans.game_question_id ?? msg.data?.question_id ?? state.currentGameQuestionId
      let parsed = null
      if (ans.text) {
        try {
          parsed = typeof ans.text === 'string' ? JSON.parse(ans.text) : ans.text
        } catch (e) {
          console.debug('No se pudo parsear answer.text como JSON:', e)
          parsed = null
        }
      }
      // parsed debe ser array de objetos con original_answer_id y guessed_player_id
      // Ejemplo: [{original_answer_id:128, guessed_player_id:171}, ...]
      if (Array.isArray(parsed)) {
        // Inicializar si no existe
        if (!state.guessCounts[qid]) state.guessCounts[qid] = {}
        for (const item of parsed) {
          if (!item?.original_answer_id || !item?.guessed_player_id) continue
          const aid = String(item.original_answer_id)
          const pid = String(item.guessed_player_id)
          if (!state.guessCounts[qid][aid]) state.guessCounts[qid][aid] = {}
          state.guessCounts[qid][aid][pid] = (state.guessCounts[qid][aid][pid] || 0) + 1
        }
        // For charting, you can get for each song: state.guessCounts[qid][original_answer_id]
      }
    }
  } catch (e) {
    console.error('Error calculando conteo de guesses en handle_NEW_ANSWER', e)
  }
}
function handle_GUESS_UPDATED(msg) {
  console.log('GUESS_UPDATED RECEIVED', msg.data)
  const qid = msg.data?.question_id
  const mapping = msg.data?.guesses || {}
  if (qid == null) return
  // replace mapping for this question
  state.guesses[qid] = mapping
}

function handle_PLAYER_LEFT(msg) {
  state.game.players = (state.game.players || []).filter(p => p.id !== msg.data.player_id)
}

function handle_QUESTION_CHANGED(msg) {
  state.currentPhaseQuestionIndex = msg.data.question_index ?? 0
  console.log("Índice de la pregunta actual:", state.currentPhaseQuestionIndex)
  // Resetear contador y lista de ids cuando cambia la pregunta
  state.currentQuestionAnswersCount = 0
  state._seenAnswerIds.splice(0)
  // If server provided a specific game_question_id (used in phase 2), store it
  if (msg.data?.game_question_id) {
    state.currentGameQuestionId = msg.data.game_question_id
  } else {
    state.currentGameQuestionId = null
  }
  // also accept an optional text for the selected game question
  state.currentGameQuestionText = msg.data?.game_question_text || null
}

function handle_GAME_UPDATED(msg) {
  const prevPlayers = state.game.players || []
  state.game = msg.data.game
  state.game.players = (msg.data.game.players || []).map(p => {
    const existing = prevPlayers.find(pl => pl.id === p.id)
    return { ...p, group: existing?.group ?? null }
  })
  console.log("GAME_UPDATED RECEIVED:", state.game)
}

async function handle_PHASE_CHANGED(msg, router) {
  state.game.phase = msg.data.phase
  console.log("Fase de la partida actualizada:", state.game.phase)

  const isAdminRoute = router.currentRoute.value.path.startsWith('/admin/')
  const base = isAdminRoute ? '/admin' : '/player'

  if (state.game?.code) {
    router.push({ path: `${base}/${state.game.code}/${state.game.phase}` })
  }

  state.phaseQuestions = []
  state.currentPhaseQuestionIndex = 0
  // Resetear contador al cambiar de fase
  state.currentQuestionAnswersCount = 0
  state._seenAnswerIds.splice(0)
  await getPhaseQuestions(router)
  state.currentGameQuestionId = state.phaseQuestions.length > 0 ? state.phaseQuestions[0].id : null
  //setup currentGameQuestionText depending on currentGameQuestionId

  console.log("Current Game Question ID:", state.currentGameQuestionId)
  if (state.currentGameQuestionId) {
    state.currentGameQuestionText = state.phaseQuestions.find(gq => gq.id === state.currentGameQuestionId)?.text || null
  } else {
    state.currentGameQuestionText = null
  }

  console.log("Current Game Question Text:", state.currentGameQuestionText)
  
}

function handle_PLAYER_JOINED(msg) {
  const prevPlayers = state.game.players || []
  state.game = msg.data.game
  state.game.players = (msg.data.game.players || []).map(p => {
    const existing = prevPlayers.find(pl => pl.id === p.id)
    return { ...p, group: existing?.group ?? null }
  })
}
//*************************************************************************************************************/

// Utils de hidratación antes de usar APIs que requieren game.code/phase
async function ensureHydrated(router) {
  if (state.game?.code) return

  // Intentar desde la ruta
  const gameCodeFromRoute = router?.currentRoute?.value?.params?.gameId
  if (gameCodeFromRoute && !state.connected && !state.ws) {
    const session = loadSession()
    const playerName = session?.playerName || 'guest'
    const role = session?.role || (router.currentRoute.value.path.startsWith('/admin/') ? 'admin' : 'player')
    connect(String(gameCodeFromRoute), playerName, router, role)
  }

  // Si ya está conectado pero sin snapshot, pedirlo
  if (state.connected && !state.game?.code) requestSync()

  // Esperar a que llegue el snapshot (con timeout)
  await waitFor(() => !!state.game?.code, 3000)
}

function waitFor(predicate, timeoutMs = 2000, intervalMs = 100) {
  return new Promise((resolve, reject) => {
    const start = Date.now()
    const tick = () => {
      if (predicate()) return resolve(true)
      if (Date.now() - start > timeoutMs) return reject(new Error('Timeout waiting for condition'))
      setTimeout(tick, intervalMs)
    }
    tick()
  })
}

function getPlayers() {
  // return all players but administrator
  return (state.game.players || []).filter(p => !p.is_admin)
}

async function getPhaseQuestions(router) {
  try {
    await ensureHydrated(router)
  } catch {
    console.warn('No se pudo hidratar game antes de cargar preguntas', state.game)
    return
  }
  if (!state.game?.code || !state.game?.phase) {
    console.warn("Faltan datos de juego para cargar preguntas", state.game)
    return
  }
  const response = await fetch(`${API_URL}/games/${state.game.code}/phases/${state.game.phase}/questions`)
  if (!response.ok) throw new Error("Error loading questions")
  const data = await response.json()
  state.phaseQuestions = data.questions || []
  console.log("Preguntas:", state.phaseQuestions)
  // reset answers counter when loading questions
  state.currentQuestionAnswersCount = 0
  state._seenAnswerIds.splice(0)
  // reset guesses mapping
  state.guesses = {}
}

async function getCurrentPhaseQuestion(router) {
  if (state.phaseQuestions.length === 0) {
    await getPhaseQuestions(router)
  }
  //console.log("Índice de la pregunta actual:", state.currentPhaseQuestionIndex)
  return state.phaseQuestions[state.currentPhaseQuestionIndex] || null
}

async function getAnswersForGameQuestion(gq_id) {
  if (!state.game?.code) throw new Error('Game not hydrated')

  debugger;
  //get questions from previous phase
  const res2 = await fetch(`${API_URL}/games/${state.game.code}/phases/${1}/game_questions`)
  const questionsFromPhase1 = await res2.json()

  //get question corresponding to the current index
  const questionPhase1 = questionsFromPhase1.game_questions[state.currentPhaseQuestionIndex]

  const res = await fetch(`${API_URL}/game_questions/${questionPhase1.id}/answers`)
  if (!res.ok) throw new Error('Error loading answers')
  const data = await res.json()
  console.log("Answers for Game Question", gq_id, data.answers)
  return data.answers || []
}

function getQuestionCount(){
  return state.phaseQuestions.length
}

// Opcional: helpers para admin
function changePhase(nextPhase) {
  send(events.ADMIN_EVENTS.CHANGE_PHASE, { phase: nextPhase })
}
function changeQuestion(nextIndex, extra = {}) {
  send(events.ADMIN_EVENTS.CHANGE_QUESTION, { question_index: nextIndex, ...extra })
}

async function submitAnswer(answer) {
  console.log("🎵 Enviando respuesta al websocket:", answer)
  await send(events.PLAYER_EVENTS.SEND_ANSWER, { answer: answer })
}

export default {
  state,
  connect,
  disconnect,
  send,
  initFromStorage,
  requestSync,
  getPlayers,
  getPhaseQuestions,
  getCurrentPhaseQuestion,
  getQuestionsForPhase,
  changePhase,
  changeQuestion,
  submitAnswer,
  getAnswersForGameQuestion,
  getQuestionCount
}

async function getQuestionsForPhase(phase) {
  if (!state.game?.code) throw new Error('Game not hydrated')
  const res = await fetch(`${API_URL}/games/${state.game.code}/phases/${phase}/game_questions`)
  if (!res.ok) throw new Error('Error loading game questions for phase')
  const data = await res.json()
  return data.game_questions || []
}