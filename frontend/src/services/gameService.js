import { reactive } from 'vue'
import Game from '../models/Game.js'
import * as events from '../constants/events.js'

const state = reactive({
  ws: null,
  connected: false,
  game: new Game()
})

function connect(gameId, playerName) {
  if (state.ws) {
    console.warn("Ya existe una conexión WebSocket activa.")
    return
  }

  const ws = new WebSocket(`ws://localhost:8000/ws/${gameId}`)
  state.ws = ws

  ws.onopen = () => {
    state.connected = true
    console.log(`✅ Conectado al WebSocket (partida ${gameId})`)

    ws.send(JSON.stringify({
      action: events.CLIENT_EVENTS.JOIN_GAME,
      player: playerName
    }))
  }

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data)
    console.log("Mensaje recibido:", msg)

    if (msg.type === events.SERVER_EVENTS.PLAYER_JOINED) {
      state.game.players = msg.data.game.players.map(p => {
        const existing = state.game.players?.find(pl => pl.id === p.id)
        return {
          ...p,
          group: existing?.group ?? null
        }
      })
      console.log("Jugadores actualizados:", state.game.players)
    }
  }



  ws.onclose = () => {
    console.log("🔌 WebSocket cerrado")
    state.connected = false
    state.ws = null
  }
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

function getPlayers() {
  //return all players but administrator
  return state.game.players.filter(p => !p.is_admin)
}

export default {
  state,
  connect,
  disconnect,
  getPlayers,
  send
}


