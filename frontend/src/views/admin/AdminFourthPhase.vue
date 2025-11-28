<template>
  <div class="min-screen flex-center">
    <div class="card flex flex-col items-center gap-6">

      <!-- Título -->
      <h1 class="text-4xl font-bold text-white text-center">
        Fase 4: Canta la canción
      </h1>

      <div class="text-center mt-10 w-full max-w-md">
          <h2 class="text-2xl font-bold mb-6"> Una pregunta normal y corriente con bastante texto{{ question }}</h2>
      </div>

      

      <!-- Botón de iniciar juego -->
      <button
        class="button-comic w-full max-w-xs"
        @click="comenzarJuego"
        :disabled="players.length === 0 || !allPlayersAssigned()"
      >
        Siguiente pregunta
      </button>

    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { onMounted, onUnmounted } from 'vue'
import gameService from '../../services/gameService'


const players = reactive([])

onMounted(() => {
  loadPlayers()
  const intervalId = setInterval(() => {
    loadPlayers()
  }, 1000)
  onUnmounted(() => {
    clearInterval(intervalId)
  })
})

function loadPlayers() {
  players.splice(0, players.length, ...gameService.getPlayers())
}

// Nombres de los grupos
const groupAName = ref('Grupo A')
const groupBName = ref('Grupo B')

// Función para asignar jugador a un grupo
function assignGroup(player, group) {
  player.group = group
}

function playersByGroup(group) {
  return players.filter(p => p.group === group  )
}

function allPlayersAssigned(){
  console.log("Verificando asignaciones de jugadores...");
  players.forEach(p => {
    console.log(`Jugador: ${p.nombre}, Grupo: ${p.group}`);
  });
  return players.every(p => p.group !== null)
}

// Función de inicio del juego
function comenzarJuego() {
  console.log('Juego iniciado con los grupos:')
  console.log(groupAName.value, playersByGroup('A'))
  console.log(groupBName.value, playersByGroup('B'))
  alert('¡Juego iniciado! Mira la consola para detalles.')
}
</script>

<style scoped>
/* Si quieres, puedes añadir un pequeño ajuste de hover en los botones ya marcados */
.button-comic.bg-green-600:hover {
  background-color: #17a34a; /* Verde más intenso al pasar el mouse */
}
</style>
