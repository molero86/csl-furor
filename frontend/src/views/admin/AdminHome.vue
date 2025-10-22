<template>
  <div class="min-screen flex-center">
    <div class="card flex flex-col items-center gap-6">

      <!-- Título -->
      <h1 class="text-4xl font-bold text-white text-center">
        Panel de Administrador
      </h1>

      <!-- Lista de jugadores -->
      <div class="w-full max-w-md">
        <h2 class="text-xl font-semibold mb-2 text-white text-center">Jugadores Conectados</h2>
        <ul class="player-list mb-4">
          <li
            v-for="(player, index) in jugadores"
            :key="index"
            class="grid grid-cols-[1fr_auto] items-center gap-4 py-1"
          >
            <span>{{ player.nombre }}</span>
            <div class="flex gap-2">
              <button
                @click="asignarGrupo(player, 'A')"
                :class="[
                  'button-comic px-2 py-1 text-sm',
                  player.grupo === 'A' ? 'highglight-button' : ''
                ]"
              >
                A
              </button>
              <button
                @click="asignarGrupo(player, 'B')"
                :class="[
                  'button-comic px-2 py-1 text-sm',
                  player.grupo === 'B' ? 'highglight-button' : '',
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
          <input v-model="nombreGrupoA" class="input-comic" placeholder="Grupo A" />
        </div>
        <div class="flex gap-2 items-center">
          <span class="text-white font-semibold">Nombre Grupo B:</span>
          <input v-model="nombreGrupoB" class="input-comic" placeholder="Grupo B" />
        </div>
      </div>

      <!-- Resumen de asignaciones -->
      <div class="flex flex-col gap-2 w-full max-w-md text-white">
        <p>Jugadores en {{ nombreGrupoA }}: {{ jugadoresEnGrupo('A').map(p => p.nombre).join(', ') || '-' }}</p>
        <p>Jugadores en {{ nombreGrupoB }}: {{ jugadoresEnGrupo('B').map(p => p.nombre).join(', ') || '-' }}</p>
      </div>

      <!-- Botón de iniciar juego -->
      <button
        class="button-comic w-full max-w-xs"
        @click="comenzarJuego"
        :disabled="jugadores.length === 0 || !allPlayersAssigned()"
      >
        Comenzar Juego
      </button>

    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'

// Lista simulada de jugadores conectados
const jugadores = reactive([
  { nombre: 'Ruben', grupo: null },
  { nombre: 'Ana', grupo: null },
  { nombre: 'Luis', grupo: null },
  { nombre: 'Marta', grupo: null },
])

// Nombres de los grupos
const nombreGrupoA = ref('Grupo A')
const nombreGrupoB = ref('Grupo B')

// Función para asignar jugador a un grupo
function asignarGrupo(player, grupo) {
  player.grupo = grupo
}

// Filtrar jugadores por grupo
function jugadoresEnGrupo(grupo) {
  return jugadores.filter(p => p.grupo === grupo)
}

function jugadorEnGrupo(player){
  return player.grupo
}

function allPlayersAssigned(){
  console.log("Verificando asignaciones de jugadores...");
  jugadores.forEach(p => {
    console.log(`Jugador: ${p.nombre}, Grupo: ${p.grupo}`);
  });
  return jugadores.every(p => p.grupo !== null)
}

// Función de inicio del juego
function comenzarJuego() {
  console.log('Juego iniciado con los grupos:')
  console.log(nombreGrupoA.value, jugadoresEnGrupo('A'))
  console.log(nombreGrupoB.value, jugadoresEnGrupo('B'))
  alert('¡Juego iniciado! Mira la consola para detalles.')
}
</script>

<style scoped>
/* Si quieres, puedes añadir un pequeño ajuste de hover en los botones ya marcados */
.button-comic.bg-green-600:hover {
  background-color: #17a34a; /* Verde más intenso al pasar el mouse */
}
</style>
