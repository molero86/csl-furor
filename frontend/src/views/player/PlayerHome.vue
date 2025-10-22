<template>
  <div class="min-screen flex-center bg-spotify-gradient px-4">
    <div class="bg-white/10 p-8 rounded-3xl w-full max-w-md flex flex-col items-center shadow-lg">
      <!-- Título -->
      <h1 class="text-title mb-6 text-white text-center">🎶 CSL Furor! 🎶</h1>
      <p class="text-subtitle mb-6 text-center">Introduce tu nombre para unirte al juego</p>

      <!-- Input y botón -->
      <div class="flex flex-col gap-4">
        <input
          v-model="nombre"
          placeholder="Tu nombre"
          class="input-comic"
        />
        <button @click="unirse" class="button-comic">
          Unirme al juego
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const nombre = ref('')
const jugadores = ref([])

// URL del backend
const API_URL = 'http://localhost:8000/players/'

// Registrar jugador
async function unirse() {
  if (!nombre.value) return alert('Introduce tu nombre')
  try {
    await axios.post(API_URL, { name: nombre.value })
    nombre.value = ''
    await cargarJugadores()
  } catch (err) {
    console.error(err)
    alert('Error al registrarte')
  }
}

// Cargar jugadores conectados
async function cargarJugadores() {
  try {
    const res = await axios.get(API_URL)
    jugadores.value = res.data
  } catch (err) {
    console.error(err)
  }
}

// Cargar jugadores al iniciar
onMounted(() => {
  cargarJugadores()
  // Refrescar cada 3 segundos
  setInterval(cargarJugadores, 3000)
})
</script>
