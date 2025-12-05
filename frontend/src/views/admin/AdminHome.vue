<template>
  <div class="min-screen flex-center">
    <div class="card flex flex-col items-center gap-6">

      <!-- Título -->
      <h1 class="text-4xl font-bold text-white text-center">
        Panel de Administrador
      </h1>

      <!-- Código de la partida -->
      <div class="flex flex-col items-center gap-2">
        <h1 
          class="text-5xl font-bold text-yellow-400 cursor-pointer select-all hover:text-yellow-300 transition-colors"
          @click="copyGameCode"
          :title="copied ? '¡Copiado!' : 'Click para copiar'"
        >
          {{ gameId }}
        </h1>
        <span v-if="copied" class="text-green-400 text-sm font-semibold animate-fade-in">
          ¡Copiado al portapapeles!
        </span>
      </div>

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
                  player.group === groupAName ? 'highglight-button' : ''
                ]"
              >
                A
              </button>
              <button
                @click="assignGroup(player, 'B')"
                :class="[
                  'button-comic px-2 py-1 text-sm',
                  player.group === groupBName ? 'highglight-button' : '',
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
        <p>Jugadores en {{ groupAName }}: {{ playersByGroup('A').map(p => p.name).join(', ') || '-' }}</p>
        <p>Jugadores en {{ groupBName }}: {{ playersByGroup('B').map(p => p.name).join(', ') || '-' }}</p>
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
import { useRoute } from 'vue-router'
import gameService from '../../services/gameService'
const API_URL = import.meta.env.VITE_API_URL

const route = useRoute()
const gameId = ref(String(route.params.gameId || ''))
let gameId2 = ''
const copied = ref(false)


const players = reactive([])
const phase = 1 // Primera fase

onMounted(() => {
  //Get gameId from url last part http://localhost:5173/admin/LD1U5M
  gameId2 = route.path.split('/').pop()
  console.log("gameId2", gameId2)
  console.log("route.path", route.path)

  loadPlayers()
  const intervalId = setInterval(() => {
    loadPlayers()
  }, 1000)
  onUnmounted(() => {
    clearInterval(intervalId)
  })
})

function copyGameCode() {
  navigator.clipboard.writeText(gameId.value).then(() => {
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }).catch(err => {
    console.error('Error al copiar:', err)
    // Fallback para navegadores antiguos
    const textArea = document.createElement('textarea')
    textArea.value = gameId.value
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  })
}

function loadPlayers() {
  players.splice(0, players.length, ...gameService.getPlayers())
}

// Nombres de los grupos
const groupAName = ref('Grupo A')
const groupBName = ref('Grupo B')

// Función para asignar jugador a un grupo
async function assignGroup(player, group) {
  try {
    // Usar el nombre personalizado del grupo
    const groupName = group === 'A' ? groupAName.value : groupBName.value
    
    const response = await fetch(`${API_URL}/players/${player.id}/group`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ group: groupName })
    })
    
    if (!response.ok) {
      throw new Error('Error al asignar grupo')
    }
    
    const updatedPlayer = await response.json()
    player.group = updatedPlayer.group
    console.log(`✅ Jugador ${player.name} asignado al grupo ${groupName}`)
  } catch (error) {
    console.error('Error al asignar grupo:', error)
    alert('Error al asignar grupo al jugador')
  }
}

function playersByGroup(group) {
  const groupName = group === 'A' ? groupAName.value : groupBName.value
  return players.filter(p => p.group === groupName)
}

function allPlayersAssigned(){
  console.log("Verificando asignaciones de jugadores...");
  players.forEach(p => {
    console.log(`Jugador: ${p.name}, Grupo: ${p.group}`);
  });
  return players.every(p => p.group !== null && p.group !== undefined)
}

// Función de inicio del juego
async function comenzarJuego() {
  console.log('Juego iniciado con los grupos:')
  console.log(groupAName.value, playersByGroup('A'))
  console.log(groupBName.value, playersByGroup('B'))

  console.log("gameId2", gameId2)
  const response = await fetch(`${API_URL}/games/${gameId2}/generate-phase/${phase}`, {
    method: "POST",
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err.detail || "Error generating phase");
  }

  const result = await response.json();
  console.log(`✅ Fase ${phase} generada correctamente (${result.count} preguntas)`);

}
</script>

<style scoped>
/* Si quieres, puedes añadir un pequeño ajuste de hover en los botones ya marcados */
.button-comic.bg-green-600:hover {
  background-color: #17a34a; /* Verde más intenso al pasar el mouse */
}
</style>
