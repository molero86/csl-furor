<template>
  <div class="min-screen flex-center">
    <div class="card flex flex-col items-center gap-6">

      <!-- Título -->
      <h1 class="text-4xl font-bold text-white text-center">
        Fase 1: Preguntas rápidas
      </h1>

      <div class="text-center mt-10 w-full max-w-md">
        <h3 class="text-2xl font-bold mb-6">Pregunta {{ currentQuestion.order || '-' }} de {{ totalQuestions }}</h3>
        <h2 class="text-2xl font-bold mb-6">{{ currentQuestion.text || '' }}</h2>
      </div>

      <!-- Progress bar to show the number of answers received for this question -->
      <div class="w-full max-w-md">
        <label class="text-white mb-2 block">Respuestas recibidas: {{ answersReceived }} / {{ players.length }}</label>
        <div class="w-full bg-gray-700 rounded-full h-6">
          <div
            class="bg-green-500 h-6 rounded-full transition-all duration-500"
            :style="{ width: (players.length ? (answersReceived / players.length * 100) : 0) + '%' }"
          ></div>
        </div>
      </div>

      <!-- Botón de iniciar juego -->
      <button
        class="button-comic w-full max-w-xs"
        @click="siguientePregunta"
      >
        {{ buttonLabel }}
      </button>

    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import { onMounted, onUnmounted } from 'vue'
import gameService from '../../services/gameService'


const players = reactive([])
const answersReceived = computed(() => gameService.state.currentQuestionAnswersCount)

const totalQuestions = computed(() => gameService.getQuestionCount())
const currentQuestion = computed(() => {
  return gameService.state.phaseQuestions[gameService.state.currentPhaseQuestionIndex] || {}
})

const isLastQuestion = computed(() => {
  return (gameService.state.currentPhaseQuestionIndex || 0) >= Math.max(0, totalQuestions.value - 1)
})

const buttonLabel = computed(() => isLastQuestion.value ? 'Pasar a la siguiente fase' : 'Siguiente pregunta')

onMounted(async () => {
  
  loadPlayers()
  const intervalId = setInterval(() => {
    loadPlayers()
  }, 1000)

  // Ensure questions are loaded and UI reacts to gameService.state changes
  await gameService.getPhaseQuestions()

  onUnmounted(() => {
    clearInterval(intervalId)
  })
})

function loadPlayers() {
  players.splice(0, players.length, ...gameService.getPlayers())
}

function siguientePregunta() {
  if (isLastQuestion.value) {
    // avanzar de fase
    const nextPhase = (gameService.state.game?.phase || 1) + 1
    gameService.changePhase(nextPhase)
  } else {
    const nextIndex = (gameService.state.currentPhaseQuestionIndex || 0) + 1
    gameService.changeQuestion(nextIndex)
  }
}
</script>

<style scoped>
/* Si quieres, puedes añadir un pequeño ajuste de hover en los botones ya marcados */
.button-comic.bg-green-600:hover {
  background-color: #17a34a; /* Verde más intenso al pasar el mouse */
}

.answers-received-pb {
  height: 20px;
  border-radius: 10px;
  transition: width 0.5s ease-in-out;
  background: linear-gradient(90deg, #34d399, #10b981);
}

</style>
