<template>
  <div class="home-container">
    <h1 class="text-title mb-6 text-white text-center">🎶 CSL Furor! 🎶</h1>

    <div class="options">
      <!-- Crear partida -->
      <button @click="handleCreateGame" class="button-comic">Crear Partida</button>

      <!-- Unirse a partida -->
      <div class="card">
        <h2>Jugador</h2>
        <p>Introduce el ID de la partida y tu nombre para unirte</p>
        <input
          v-model="gameId"
          placeholder="ID de partida"
          class="input-comic input-id"
        />
        <input
          v-model="playerName"
          placeholder="Tu nombre"
          class="input-comic input-id"
        />
        <button
          @click="handleJoinGame"
          class="button-comic w-full"
          :disabled="!gameId.trim() || !playerName.trim()"
        >
          Unirse
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";
import { createGame, getGame } from "../services/api";
import gameService from "../services/gameService";

const router = useRouter();
const gameId = ref("");
const playerName = ref("");

async function handleCreateGame() {
  try {
    const game = await createGame();

    const playerName = "administrator";
    gameService.connect(game.code, playerName);

    router.push(`/admin/${game.code}`);
  } catch (error) {
    console.error(error);
    alert("Error al crear la partida");
  }
}

async function handleJoinGame() {
  const id = gameId.value.trim();
  const pName = playerName.value.trim();
  if (!id) return;

  try {
    const game = await getGame(id);
    if (!game) {
      alert("La partida no existe 😕");
      return;
    }

    gameService.connect(game.code, pName);
    router.push(`/player/${id}`);
  } catch (error) {
    console.error(error);
    alert("Error al unirse a la partida");
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
