<template>
  <div class="min-screen flex-center py-8">
    <div class="w-full max-w-6xl px-6">

      <!-- Título -->
      <h1 class="text-6xl font-bold text-white text-center mb-4 animate-pulse-slow">
        🏆 ¡Puntuaciones Finales! 🏆
      </h1>
      <p class="text-2xl text-white/80 text-center mb-12">
        Resultados combinados de Fase 2 y Fase 4
      </p>

      <div v-if="loading" class="text-center text-white text-2xl">
        ⏳ Cargando puntuaciones...
      </div>

      <div v-else>
        <!-- Ranking por Grupos -->
        <div v-if="groupsRanking.length > 0" class="mb-12">
          <h2 class="text-4xl font-bold text-white text-center mb-8">
            🎭 Ranking por Grupos
          </h2>
          
          <div class="ranking-grid">
            <div 
              v-for="(group, index) in groupsRanking" 
              :key="group.group_name"
              class="ranking-card group-card"
              :class="{'gold': index === 0, 'silver': index === 1, 'bronze': index === 2}"
            >
              <div class="rank-badge">{{ index + 1 }}</div>
              <div class="medal" v-if="index < 3">
                {{ index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉' }}
              </div>
              <h3 class="group-name">{{ group.group_name }}</h3>
              <p class="group-info">{{ group.player_count }} jugadores</p>
              <div class="score">{{ group.total_points }} pts</div>
            </div>
          </div>
        </div>

        <!-- Ranking Individual -->
        <div>
          <h2 class="text-4xl font-bold text-white text-center mb-8">
            👤 Ranking Individual
          </h2>
          
          <div class="ranking-grid">
            <div 
              v-for="(player, index) in playersRanking" 
              :key="player.player_id"
              class="ranking-card player-card"
              :class="{'gold': index === 0, 'silver': index === 1, 'bronze': index === 2}"
            >
              <div class="rank-badge">{{ index + 1 }}</div>
              <div class="medal" v-if="index < 3">
                {{ index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉' }}
              </div>
              <h3 class="player-name">{{ player.player_name }}</h3>
              <p class="player-group" v-if="player.group">{{ player.group }}</p>
              <div class="score">{{ player.total_points }} pts</div>
            </div>
          </div>
        </div>

        <!-- Botones de acción -->
        <div class="actions-container">
          <button
            class="button-comic text-2xl py-6 px-12"
            @click="goToHome"
          >
            🏠 Volver al Inicio
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import gameService from '../../services/gameService'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const playersRanking = ref([])
const groupsRanking = ref([])

onMounted(async () => {
  await loadScores()
})

async function loadScores() {
  loading.value = true
  try {
    // Hidratar el estado del juego desde la ruta
    const gameCode = route.params.gameId
    console.log('🎮 Cargando puntuaciones para game:', gameCode)
    
    const data = await gameService.getCombinedScores(gameCode)
    playersRanking.value = data.players || []
    groupsRanking.value = data.groups || []
    console.log('📊 Puntuaciones finales cargadas:', data)
  } catch (error) {
    console.error('❌ Error cargando puntuaciones:', error)
    alert('Error al cargar las puntuaciones finales')
  } finally {
    loading.value = false
  }
}

function goToHome() {
  const gameCode = route.params.gameId
  router.push(`/admin/${gameCode}/home`)
}
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.animate-pulse-slow {
  animation: pulse-slow 2s ease-in-out infinite;
}

.ranking-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.ranking-card {
  position: relative;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 1.5rem;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ranking-card:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.ranking-card.gold {
  border-color: #fbbf24;
  background: linear-gradient(145deg, rgba(251, 191, 36, 0.2), rgba(251, 191, 36, 0.05));
  box-shadow: 0 10px 30px rgba(251, 191, 36, 0.4);
}

.ranking-card.silver {
  border-color: #cbd5e1;
  background: linear-gradient(145deg, rgba(203, 213, 225, 0.2), rgba(203, 213, 225, 0.05));
  box-shadow: 0 10px 30px rgba(203, 213, 225, 0.3);
}

.ranking-card.bronze {
  border-color: #fb923c;
  background: linear-gradient(145deg, rgba(251, 146, 60, 0.2), rgba(251, 146, 60, 0.05));
  box-shadow: 0 10px 30px rgba(251, 146, 60, 0.3);
}

.rank-badge {
  position: absolute;
  top: -15px;
  left: -15px;
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 900;
  color: white;
  border: 3px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.gold .rank-badge {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
}

.silver .rank-badge {
  background: linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%);
}

.bronze .rank-badge {
  background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
}

.medal {
  font-size: 4rem;
  margin-bottom: 1rem;
  animation: bounce 1s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.group-name,
.player-name {
  font-size: 2rem;
  font-weight: 900;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.group-info {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 1rem;
}

.player-group {
  font-size: 1.125rem;
  color: #fbbf24;
  font-weight: 600;
  margin-bottom: 1rem;
}

.score {
  font-size: 3rem;
  font-weight: 900;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 4px 8px rgba(251, 191, 36, 0.3);
}

.actions-container {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 4rem;
  flex-wrap: wrap;
}
</style>
