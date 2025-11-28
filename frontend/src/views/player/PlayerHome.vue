<template>
  <div class="min-screen flex-center bg-spotify-gradient px-4 overflow-hidden relative">
    <div
      v-for="(player, index) in players"
      :key="index"
      class="absolute player-bubble text-white text-lg font-bold px-4 py-2 rounded-full shadow-lg"
      :style="getRandomPosition(index)"
    >
      {{ player.name }}
    </div>

    <div class="absolute bottom-8 w-full text-center text-white/70 waiting-text">
      Esperando a que se unan los jugadores...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import gameService from '../../services/gameService.js'

const players = ref([])

// Función para obtener una posición inicial aleatoria
function getRandomPosition(index) {
  const top = Math.random() * 80 + 10 // entre 10% y 90%
  const left = Math.random() * 80 + 10
  const delay = Math.random() * 2 // retraso aleatorio
  const duration = 10 + Math.random() * 10 // velocidad distinta
  const color = `hsl(${Math.random() * 360}, 70%, 60%)`
  return {
    top: `${top}%`,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    color
  }
}

function cargarJugadores() {
  // players.value = ["Jugador 1", "Jugador 2", "Jugador 3", "Jugador 4"]
  players.value = gameService.getPlayers()
  const intervalId = setInterval(() => {
    players.value = gameService.getPlayers()
  }, 1000)
  onUnmounted(() => {
    clearInterval(intervalId)
  })
}

onMounted(() => {
  cargarJugadores()
  setInterval(cargarJugadores, 5000)
})
</script>

<style scoped>
.player-bubble {
  animation-name: bounceAround;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
  will-change: transform;
  font-size: larger;
  font-weight: bold;
  font-family: 'Comic Sans MS', cursive, sans-serif;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

/* Animación de rebote */
@keyframes bounceAround {
  0%   { transform: translate(0, 0); }
  25%  { transform: translate(10vw, 10vh); }
  50%  { transform: translate(30vw, 30vh); }
  75%  { transform: translate(20vw, 20vh); }
  100% { transform: translate(10vw, 10vh); }
}

.waiting-text {
  font-size: 1.55rem;
  animation: pulse 2s infinite;
}
</style>
