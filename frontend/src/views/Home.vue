<template>
  <div class="home-container">
    <!-- Título -->
    <h1 class="text-title mb-6 text-white text-center">🎶 CSL Furor! 🎶</h1>

    <div class="options">
      <!-- Crear partida -->
      <button @click="createGame" class="button-comic">Crear Partida</button>

      <!-- Unirse a partida -->
      <div class="card">
        <h2>Jugador</h2>
        <p>Introduce el ID de la partida para unirte</p>
        <input
          v-model="gameId"
          placeholder="ID de partida"
          class="input-comic input-id"
        />
        <button
          @click="joinGame"
          class="button-comic w-full"
          :disabled="!gameId.trim()"
        >
          Unirse
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref } from 'vue'

const router = useRouter()
const gameId = ref('')

// Genera un ID de partida aleatorio (por ejemplo, 6 caracteres)
function generateGameId() {
  return Math.random().toString(36).substring(2, 8).toUpperCase()
}

function createGame() {
  const id = generateGameId()
  router.push(`/admin/${id}`)
}

function joinGame() {
  if (gameId.value.trim()) {
    router.push(`/player/${gameId.value.trim()}`)
  }
}
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}

.title {
  font-size: 2.5rem;
  margin-bottom: 3rem;
  color: #222;
  text-align: center;
}

.options {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2rem;
}

.card {
  background-color: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  width: 300px;
  text-align: center;
}

.card h2 {
  margin-bottom: 1rem;
}

.card p {
  margin-bottom: 1.5rem;
  color: #000000;
}

.input-id {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 0.5rem;
  text-align: center;
}
</style>
