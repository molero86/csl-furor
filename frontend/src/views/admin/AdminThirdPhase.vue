<template>
  <div class="min-screen flex-center py-8">
    <div class="w-full max-w-6xl px-6">

      <!-- Título Principal -->
      <div class="text-center mb-12">
        <h1 class="text-6xl font-black text-white mb-4 animate-pulse-slow">
          🏆 RESULTADOS FASE 2 🏆
        </h1>
        <p class="text-xl text-white/70">¿Quién conoce mejor a quién?</p>
      </div>

      <div v-if="loading" class="text-center text-white/60 text-2xl">
        Cargando puntuaciones...
      </div>

      <div v-else class="space-y-12">
        <!-- Ranking Individual -->
        <div class="ranking-section">
          <div class="section-header">
            <h2 class="text-4xl font-bold text-white mb-2">👥 Ranking Individual</h2>
            <div class="header-line"></div>
          </div>
          
          <div v-if="playersRanking.length === 0" class="text-white/60 text-center text-xl py-8">
            No hay puntuaciones disponibles
          </div>
          
          <div v-else class="grid gap-4">
            <div 
              v-for="(player, index) in playersRanking" 
              :key="player.player_id"
              :class="[
                'player-card',
                { 'top-1': index === 0, 'top-2': index === 1, 'top-3': index === 2 }
              ]"
            >
              <div class="flex items-center gap-6 flex-1">
                <div class="position-badge" :class="getMedalClass(index)">
                  <span class="position-number">{{ index + 1 }}</span>
                  <span class="medal-icon">{{ getMedalIcon(index) }}</span>
                </div>
                <div class="player-info">
                  <div class="player-name">{{ player.player_name }}</div>
                  <div v-if="player.group" class="player-group">Grupo {{ player.group }}</div>
                </div>
              </div>
              <div class="score-badge">
                <div class="score-number">{{ player.total_points }}</div>
                <div class="score-label">puntos</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Ranking por Grupos -->
        <div v-if="groupsRanking.length > 0" class="ranking-section">
          <div class="section-header">
            <h2 class="text-4xl font-bold text-white mb-2">🏢 Ranking por Grupos</h2>
            <div class="header-line"></div>
          </div>
          
          <div class="grid gap-4">
            <div 
              v-for="(group, index) in groupsRanking" 
              :key="group.group"
              :class="[
                'group-card',
                { 'top-1': index === 0, 'top-2': index === 1, 'top-3': index === 2 }
              ]"
            >
              <div class="flex items-center gap-6 flex-1">
                <div class="position-badge" :class="getMedalClass(index)">
                  <span class="position-number">{{ index + 1 }}</span>
                  <span class="medal-icon">{{ getMedalIcon(index) }}</span>
                </div>
                <div class="player-info">
                  <div class="player-name">Grupo {{ group.group }}</div>
                  <div class="player-group">{{ group.players_count }} jugadores</div>
                </div>
              </div>
              <div class="score-badge">
                <div class="score-number">{{ group.total_points }}</div>
                <div class="score-label">puntos</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Botón para continuar -->
        <div class="text-center mt-12">
          <button
            class="button-comic text-2xl py-6 px-12"
            @click="continuarJuego"
          >
            Continuar a Fase 3 →
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import gameService from '../../services/gameService'

const loading = ref(true)
const playersRanking = ref([])
const groupsRanking = ref([])
const totalQuestions = ref(0)

onMounted(async () => {
  await loadScores()
})

async function loadScores() {
  loading.value = true
  try {
    const data = await gameService.getPhase2Scores()
    playersRanking.value = data.players || []
    groupsRanking.value = data.groups || []
    totalQuestions.value = data.total_questions || 0
    
    console.log('📊 Ranking cargado:', {
      players: playersRanking.value.length,
      groups: groupsRanking.value.length,
      questions: totalQuestions.value
    })
  } catch (error) {
    console.error('❌ Error cargando puntuaciones:', error)
  } finally {
    loading.value = false
  }
}

function continuarJuego() {
  // TODO: Implementar lógica para continuar a la fase 3 real
  console.log('Continuando a fase 3...')
  alert('Fase 3: Completar canción - Por implementar')
}

function getMedalIcon(index) {
  if (index === 0) return '🥇'
  if (index === 1) return '🥈'
  if (index === 2) return '🥉'
  return '🎖️'
}

function getMedalClass(index) {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

.ranking-section {
  margin-bottom: 3rem;
  margin-left: 100px;
  margin-right: 100px;
}

.section-header {
  text-align: center;
  margin-bottom: 2rem;
}

.header-line {
  height: 4px;
  background: linear-gradient(90deg, transparent, #fbbf24, transparent);
  margin: 0 auto;
  width: 60%;
  border-radius: 2px;
}

.player-card,
.group-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.player-card:hover,
.group-card:hover {
  transform: translateX(8px);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(251, 191, 36, 0.5);
  box-shadow: 0 8px 32px rgba(251, 191, 36, 0.2);
}

.player-card.top-1,
.group-card.top-1 {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.15), rgba(255, 255, 255, 0.08));
  border: 3px solid #fbbf24;
  box-shadow: 0 8px 32px rgba(251, 191, 36, 0.3);
  transform: scale(1.02);
}

.player-card.top-2,
.group-card.top-2 {
  background: linear-gradient(135deg, rgba(192, 192, 192, 0.15), rgba(255, 255, 255, 0.08));
  border: 2px solid #c0c0c0;
}

.player-card.top-3,
.group-card.top-3 {
  background: linear-gradient(135deg, rgba(205, 127, 50, 0.15), rgba(255, 255, 255, 0.08));
  border: 2px solid #cd7f32;
}

.position-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.2);
}

.position-badge.gold {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  border-color: #fbbf24;
  box-shadow: 0 0 20px rgba(251, 191, 36, 0.5);
}

.position-badge.silver {
  background: linear-gradient(135deg, #e5e7eb, #9ca3af);
  border-color: #c0c0c0;
}

.position-badge.bronze {
  background: linear-gradient(135deg, #f59e0b, #cd7f32);
  border-color: #cd7f32;
}

.position-number {
  font-size: 1.5rem;
  font-weight: 900;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.medal-icon {
  font-size: 1.75rem;
  line-height: 1;
}

.player-info {
  flex: 1;
}

.player-name {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.25rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.player-group {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.score-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(34, 197, 94, 0.1));
  border-radius: 0.75rem;
  border: 2px solid rgba(34, 197, 94, 0.3);
  min-width: 120px;
}

.score-number {
  font-size: 2.5rem;
  font-weight: 900;
  color: #22c55e;
  line-height: 1;
  text-shadow: 0 2px 8px rgba(34, 197, 94, 0.4);
}

.score-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.05em;
  margin-top: 0.25rem;
}

.button-comic {
  font-size: 1.5rem !important;
  padding: 1.5rem 3rem !important;
  transition: all 0.3s ease;
}

.button-comic:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 32px rgba(251, 191, 36, 0.4);
}
</style>
