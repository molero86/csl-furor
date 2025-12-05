<template>
  <div class="min-screen flex-center bg-spotify-gradient px-4 overflow-hidden relative">
    
    <!-- Intro inicial -->
    <transition name="fade">
      <div v-if="showIntro" class="absolute bottom-8 w-full text-center text-white/70 waiting-text">
        <h1>Fase 4. Canta la canción</h1>
      </div>

      <!-- Pantalla principal - Botón de Buzzer -->
      <div v-else class="flex flex-col justify-center items-center w-full h-full py-10 text-white">
        
        <!-- Mensaje de estado -->
        <div v-if="buzzerWinner" class="text-center mb-8">
          <h2 class="text-4xl font-bold mb-4">
            {{ buzzerWinner.player_name === playerName ? '¡Tú respondes!' : `Responde: ${buzzerWinner.player_name}` }}
          </h2>
          <p class="text-2xl text-white/70">
            {{ buzzerWinner.player_name === playerName ? '🎤' : '⏳ Espera tu turno' }}
          </p>
        </div>

        <!-- Botón de Buzzer -->
        <div v-if="!buzzerWinner" class="buzzer-container">
          <button
            class="buzzer-button"
            :class="{ 'buzzer-disabled': !buzzerEnabled }"
            @click="pressBuzzer"
            :disabled="!buzzerEnabled"
          >
            <div class="buzzer-content">
              <div class="buzzer-icon">🔔</div>
              <div class="buzzer-text">{{ buzzerEnabled ? '¡PRESIONA!' : 'ESPERANDO...' }}</div>
            </div>
          </button>
          <p class="buzzer-hint">Presiona cuando la canción termine</p>
        </div>

        <!-- Indicador de espera si ya presionó -->
        <div v-else-if="!buzzerWinner && !buzzerEnabled" class="text-center">
          <div class="text-6xl mb-4 animate-pulse">⏳</div>
          <p class="text-2xl">Esperando...</p>
        </div>

      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import gameService from '../../services/gameService'

const showIntro = ref(true)
const playerName = ref('')

// Estado del buzzer desde gameService
const buzzerWinner = computed(() => gameService.state.buzzerWinner)
const buzzerEnabled = computed(() => gameService.state.buzzerEnabled)

function pressBuzzer() {
  if (!buzzerEnabled.value) return
  
  const success = gameService.pressBuzzer(playerName.value)
  if (success) {
    console.log('🔔 Buzzer presionado por:', playerName.value)
  }
}

onMounted(() => {
  // Obtener el nombre del jugador del estado
  playerName.value = gameService.state.player?.name || 'Jugador'
  
  setTimeout(() => {
    showIntro.value = false
  }, 3000)
})

// Watch para log de cambios en el estado del buzzer
watch(buzzerWinner, (newWinner) => {
  if (newWinner) {
    console.log('🏆 Ganador del buzzer:', newWinner.player_name)
  }
})

watch(buzzerEnabled, (enabled) => {
  console.log('🔔 Buzzer habilitado:', enabled)
})
</script>

<style scoped>
.waiting-text {
  font-size: 1.55rem;
  animation: pulse 2s infinite;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.8s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.buzzer-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

.buzzer-button {
  width: 320px;
  height: 320px;
  border-radius: 50%;
  border: 8px solid #fbbf24;
  background: linear-gradient(145deg, #fbbf24, #f59e0b);
  box-shadow: 
    0 20px 60px rgba(251, 191, 36, 0.6),
    inset 0 -10px 30px rgba(0, 0, 0, 0.3),
    inset 0 10px 30px rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.buzzer-button:hover:not(.buzzer-disabled) {
  transform: scale(1.05);
  box-shadow: 
    0 25px 70px rgba(251, 191, 36, 0.8),
    inset 0 -10px 30px rgba(0, 0, 0, 0.3),
    inset 0 10px 30px rgba(255, 255, 255, 0.3);
}

.buzzer-button:active:not(.buzzer-disabled) {
  transform: scale(0.95);
  box-shadow: 
    0 10px 30px rgba(251, 191, 36, 0.4),
    inset 0 5px 20px rgba(0, 0, 0, 0.5);
}

.buzzer-button.buzzer-disabled {
  background: linear-gradient(145deg, #6b7280, #4b5563);
  border-color: #6b7280;
  box-shadow: 
    0 10px 30px rgba(107, 114, 128, 0.3),
    inset 0 -5px 15px rgba(0, 0, 0, 0.3);
  cursor: not-allowed;
  opacity: 0.5;
}

.buzzer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 1rem;
}

.buzzer-icon {
  font-size: 6rem;
  animation: ring 2s ease-in-out infinite;
}

@keyframes ring {
  0%, 100% { transform: rotate(0deg); }
  10% { transform: rotate(15deg); }
  20% { transform: rotate(-15deg); }
  30% { transform: rotate(10deg); }
  40% { transform: rotate(-10deg); }
  50% { transform: rotate(0deg); }
}

.buzzer-text {
  font-size: 2rem;
  font-weight: 900;
  color: white;
  text-shadow: 
    0 2px 10px rgba(0, 0, 0, 0.5),
    0 0 20px rgba(251, 191, 36, 0.5);
  letter-spacing: 0.1em;
}

.buzzer-disabled .buzzer-icon {
  animation: none;
}

.buzzer-hint {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>