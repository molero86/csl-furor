<template>
  <div class="min-screen flex-center bg-spotify-gradient px-4 overflow-hidden relative">

    <transition name="fade">
      <div v-if="showIntro" class="absolute bottom-8 w-full text-center text-white/70 waiting-text">
        <h1>Fase 2. ¿Quién respondió qué?</h1>
      </div>

      <div v-else class="flex flex-col items-center w-full h-full py-8 text-white">
        <div class="w-full max-w-3xl">
          <h2 class="text-2xl font-bold mb-4">{{ questionText }}</h2>

          <div v-if="answers.length === 0" class="text-center text-white/60">Esperando respuestas para esta pregunta...</div>

          <form @submit.prevent="submitGuesses" v-if="answers.length">
            <div v-for="ans in answers" :key="ans.id" class="mb-4 bg-white/5 p-3 rounded-lg">
              <template v-if="ans.trackName || ans.text">
                <ul class="mt-2 bg-white/10 rounded-2xl p-2 divide-y divide-white/20">
                  <li class="flex items-center gap-3 p-2 rounded-xl">
                    <img v-if="ans.artworkUrl60" :src="ans.artworkUrl60" class="w-10 h-10 rounded-lg" alt="cover" />
                    <div class="text-left">
                      <p class="font-semibold text-sm track-name">{{ ans.trackName || simplifiedTitle(ans.text) }}</p>
                      <p class="text-xs text-white/70 artist-name">{{ ans.artistName || simplifiedArtist(ans.text) }}</p>
                    </div>
                  </li>
                </ul>
              </template>

              <div class="mt-2">
                <label class="text-sm text-white block mb-1">¿Quién respondió esto?</label>
                <select v-model="selections[ans.id]" class="input-comic w-full">
                  <option :value="null">-- Seleccionar jugador --</option>
                  <option v-for="p in playersList" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
              </div>
            </div>

            <div class="flex gap-2 items-center">
              <button type="submit" class="button-comic" :disabled="submitting || sent">{{ sent ? 'Enviado' : (submitting ? 'Enviando...' : 'Enviar respuestas') }}</button>
              <div class="ml-4 text-sm text-green-300" v-if="successMessage">{{ successMessage }}</div>
            </div>
          </form>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from 'vue'
import gameService from '../../services/gameService'

const showIntro = ref(true)
const answers = ref([])
const playersList = ref([])
const selections = reactive({})
const submitting = ref(false)
const successMessage = ref('')
const sent = ref(false)

// derived question text (the selected game question in phase 2)
const questionText = ref('')

async function loadForCurrentGameQuestion(gqId = null) {
  const id = gqId ?? gameService.state.currentGameQuestionId
  if (!id) {
    answers.value = []
    questionText.value = gameService.state.currentGameQuestionText || ''
    return
  }
  
  // Resetear estado del formulario
  sent.value = false
  submitting.value = false
  successMessage.value = ''
  
  const ans = await gameService.getAnswersForGameQuestion(id)
  answers.value = ans
  // enrich answers with iTunes metadata when possible (spotify_id stores the external track id)
  await Promise.all(answers.value.map(async (a) => {
    try {
      if (a.spotify_id) {
        const res = await fetch(`https://itunes.apple.com/lookup?id=${encodeURIComponent(a.spotify_id)}`)
        if (res.ok) {
          const data = await res.json()
          if (data.results && data.results.length) {
            const s = data.results[0]
            a.artworkUrl60 = s.artworkUrl60
            a.trackName = s.trackName
            a.artistName = s.artistName
          }
        }
      }
    } catch (e) {
      console.debug('No metadata for answer', a.id, e)
    }
  }))
  // prepare selections (reset)
  Object.keys(selections).forEach(k => delete selections[k])
  answers.value.forEach(a => {
    selections[a.id] = null
  })
  playersList.value = gameService.state.game.players || []
  // optional question text from state
  questionText.value = gameService.state.currentGameQuestionText || (gameService.state.phaseQuestions.find(p => p.id === id)?.text || '')
}

function resetSelections() {
  Object.keys(selections).forEach(k => selections[k] = null)
}

async function submitGuesses() {
  // prepare guesses only for selections with a value
  const guesses = Object.keys(selections)
    .map(k => ({ answer_id: Number(k), guessed_player_id: selections[k] }))
    .filter(g => g.guessed_player_id != null)

  // require that every answer has a selected guessed player
  const allSelected = answers.value.every(a => selections[a.id] != null)
  if (!allSelected) {
    successMessage.value = 'Debes seleccionar una opción para cada respuesta antes de enviar.'
    setTimeout(() => successMessage.value = '', 3000)
    return
  }

  // prevent double sends
  if (sent.value) return

  submitting.value = true
  // Build a single Answer payload according to the Answer model.
  // The Answer.text will contain a JSON array with song info and selected user for each original answer.
  const phaseQuestionId = gameService.state.currentGameQuestionId
  if (!phaseQuestionId) {
    successMessage.value = 'No hay pregunta de fase seleccionada.'
    submitting.value = false
    return
  }

  const associations = answers.value.map(a => ({
    original_answer_id: a.id,
    text: a.text || null,
    trackName: a.trackName || null,
    artistName: a.artistName || null,
    artworkUrl60: a.artworkUrl60 || null,
    guessed_player_id: selections[a.id] || null
  }))

  const answerPayload = {
    question_id: phaseQuestionId,
    spotify_id: '',
    text: JSON.stringify(associations),
    player_name: gameService.state.player.name,
    game_code: gameService.state.game.code
  }

  // ensure websocket is connected before sending
  const ws = gameService.state.ws
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    successMessage.value = 'No conectado al servidor. Intenta reconectar.'
    setTimeout(() => successMessage.value = '', 3000)
    submitting.value = false
    return
  }

  try {
    await gameService.submitAnswer(answerPayload)
    successMessage.value = 'Enviado con éxito.'
    sent.value = true
  } catch (e) {
    console.error('Error submitting guesses as Answer', e)
    successMessage.value = 'Error al enviar. Intenta de nuevo.'
    setTimeout(() => successMessage.value = '' , 3000)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await loadForCurrentGameQuestion()
  // try to init ws session if needed
  gameService.connect && gameService.initFromStorage && gameService.initFromStorage()
  // react to changes in the selected game question
  watch(() => gameService.state.currentGameQuestionId, async (newId) => {
    await loadForCurrentGameQuestion(newId)
  })

  setTimeout(() => {
    showIntro.value = false
  }, 3000)
})

function simplifiedTitle(text) {
  if (!text) return ''
  const parts = text.split(' - ')
  return parts[0].trim()
}

function simplifiedArtist(text) {
  if (!text) return ''
  const parts = text.split(' - ')
  return parts[1] ? parts[1].trim() : ''
}
</script>

<style scoped>
.waiting-text {
  font-size: 1.55rem;
  animation: pulse 2s infinite;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.8s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
img {
  margin-right: 8px !important;
}
p {
  margin: 0 !important;
}
ul{
  list-style: none;
  margin: 1rem;
  padding: 1rem;
  width: 85%;
  max-width: 500px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 1rem;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
  color: white;
  overflow-y: auto;
  max-height: 300px;
}

.track-name {
  font-size: 1rem;
  font-weight: 500;
}
.artist-name {
  font-size: 0.85rem;
  color: #cccccc;
}

.button-comic:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #6b7280 !important;
  pointer-events: none;
}

.button-comic:disabled:hover {
  background-color: #6b7280 !important;
  transform: none !important;
}

</style>
