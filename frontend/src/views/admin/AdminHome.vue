<template>
  <div class="min-screen flex-center">
    <div class="card flex flex-col items-center gap-6">

      <!-- Título -->
      <h1 class="text-4xl font-bold text-white text-center">
        Panel de Administrador
      </h1>

      <!-- Players list -->
      <div class="w-full max-w-md">
        <h2 class="text-xl font-semibold mb-2 text-white text-center">Jugadores Conectados</h2>
        <ul class="player-list mb-4">
          <li
            v-for="(player, index) in players"
            :key="index"
            class="grid grid-cols-[1fr_auto] items-center gap-4 py-1"
          >
            <span>{{ player.name }}</span>
            <div class="flex gap-2">
              <button
                @click="assignGroup(player, 'A')"
                :class="[
                  'button-comic px-2 py-1 text-sm',
                  player.group === 'A' ? 'highglight-button' : ''
                ]"
              >
                A
              </button>
              <button
                @click="assignGroup(player, 'B')"
                :class="[
                  'button-comic px-2 py-1 text-sm',
                  player.group === 'B' ? 'highglight-button' : '',
                ]"
              >
                B
              </button>
            </div>
          </li>
        </ul>
      </div>

      <!-- Nombres de grupos editables -->
      <div class="flex flex-col gap-4 w-full max-w-md">
        <div class="flex gap-2 items-center">
          <span class="text-white font-semibold">Nombre Grupo A:</span>
          <input v-model="groupAName" class="input-comic" placeholder="Grupo A" />
        </div>
        <div class="flex gap-2 items-center">
          <span class="text-white font-semibold">Nombre Grupo B:</span>
          <input v-model="groupBName" class="input-comic" placeholder="Grupo B" />
        </div>
      </div>

      <!-- Resumen de asignaciones -->
      <div class="flex flex-col gap-2 w-full max-w-md text-white">
        <p>Jugadores en {{ groupAName }}: {{ playersByGroup('A').map(p => p.nombre).join(', ') || '-' }}</p>
        <p>Jugadores en {{ groupBName }}: {{ playersByGroup('B').map(p => p.nombre).join(', ') || '-' }}</p>
      </div>

      <!-- Botón de iniciar juego -->
      <button
        class="button-comic w-full max-w-xs"
        @click="comenzarJuego"
        :disabled="players.length === 0 || !allPlayersAssigned()"
      >
        Comenzar Juego
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
