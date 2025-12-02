<template>
  <div class="min-screen flex-center">
    <div class="card w-full max-w-4xl p-6">
      <h1 class="text-2xl font-bold mb-4">Admin - Fase 2: Adivinanzas</h1>

        <h1 class="bg-white/5 p-3 rounded">{{ currentQuestionText }}</h1>

        <h3 class="bg-white/5 p-3 rounded">Pregunta {{ currentIndex + 1 }} / {{ gameQuestions.length }}</h3>

      <div class="grid grid-cols-2 gap-4">
        <div class="flex flex-col items-center">
          <h2 class="font-semibold mb-2">Respuestas</h2>
          <ul :class="['w-full space-y-3 max-w-2xl', answers.length > 7 ? 'limited' : '']">
            <li v-for="ans in answers" :key="ans.id" class="p-3 bg-white/5 rounded">
              <div class="flex items-center gap-4">
                
                <template v-if="ans.trackName || ans.text">
                  <ul class="mt-2 bg-white/10 rounded-2xl p-2 divide-y divide-white/20">
                    <li class="flex items-center gap-3 p-2 rounded-xl answer-item">
                      <img v-if="ans.artworkUrl60" :src="ans.artworkUrl60" class="w-10 h-10 rounded-lg" alt="cover" />
                      <div class="text-left">
                        <p class="font-semibold text-sm track-name">{{ ans.trackName || simplifiedTitle(ans.text) }}</p>
                        <p class="text-xs text-white/70 artist-name">{{ ans.artistName || simplifiedArtist(ans.text) }}</p>
                      </div>
                    </li>
                  </ul>
                </template>

                <div class="w-48 text-sm">
                  <div v-if="guessesByAnswer[ans.id] && guessesByAnswer[ans.id].length">
                    <div v-for="g in guessesByAnswer[ans.id]" :key="g.id" class="mb-1">
                      {{ playerName(g.guessed_player_id) }} <span class="text-white/60">(por {{ playerName(g.player_id) }})</span>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>
        <div>
          <h2 class="font-semibold mb-2">Estadísticas</h2>
          <ul class="space-y-3">
            <li v-for="ans in answers" :key="ans.id" class="p-2 bg-white/5 rounded">
              <div class="flex items-center gap-3">
                <div class="flex-1">
                  <div v-if="hasCountsForAnswer(ans.id)">
                    <div v-for="item in countsForAnswerArray(ans.id)" :key="item.playerId" class="flex items-center gap-2 mb-1">
                      <div class="text-xs w-24">{{ item.name }}</div>
                      <div class="flex-1 bg-white/10 rounded h-4">
                        <div :style="{ width: item.percent + '%'}" class="h-4 bg-green-500 rounded"></div>
                      </div>
                      <div class="text-xs w-6 text-right">{{ item.count }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-4">
        <label class="text-sm text-white block">Respuestas recibidas: {{ answers.length }} / {{ players.length }}</label>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import gameService from '../../services/gameService'

const players = ref([])
const answers = ref([])
const guessesByAnswer = ref({})
const counts = ref({})
const guessCountsState = ref({}) // mirrors gameService.state.guessCounts for reactivity
const gameQuestions = ref([])
const currentIndex = ref(0)

const currentQuestionText = computed(() => gameService.state.currentGameQuestionText || '')

function playerName(id) {
  const p = (gameService.state.game.players || []).find(x => x.id === id)
  return p ? p.name : '—'
}

function simplifiedTitle(text) {
  if (!text) return ''
  const parts = text.split(' - ')
  return parts[0].trim()
}

function simplifiedArtist(text) {
  if (!text) return ''
  const parts = text.split(' - ')
  return parts[1] ? parts[1].trim() : ''
}

function hasCountsForAnswer(ansId) {
  const gqId = gameService.state.currentGameQuestionId || (gameQuestions.value[currentIndex.value] && gameQuestions.value[currentIndex.value].id)
  if (!gqId) return false
  return !!(guessCountsState.value[gqId] && guessCountsState.value[gqId][String(ansId)])
}

function countsForAnswerArray(ansId) {
  const gqId = gameService.state.currentGameQuestionId || (gameQuestions.value[currentIndex.value] && gameQuestions.value[currentIndex.value].id)
  if (!gqId) return []
  const obj = (guessCountsState.value[gqId] && guessCountsState.value[gqId][String(ansId)]) || {}
  const arr = Object.entries(obj).map(([pid, count]) => ({ playerId: pid, name: playerName(Number(pid)), count }))
  if (arr.length === 0) return []
  const max = Math.max(...arr.map(x => x.count), 1)
  return arr.map(x => ({ ...x, percent: Math.round((x.count / max) * 100) })).sort((a, b) => b.count - a.count)
}

async function load(gqId = null) {
  players.value = gameService.state.game.players || []
  // load list of game questions from phase 1 to iterate
  gameQuestions.value = await gameService.getQuestionsForPhase(1)

  const targetId = gqId ?? gameService.state.currentGameQuestionId ?? (gameQuestions.value[currentIndex.value] && gameQuestions.value[currentIndex.value].id)
  if (!targetId) return

  // set currentIndex to match if possible
  const idx = gameQuestions.value.findIndex(g => g.id === targetId)
  if (idx >= 0) currentIndex.value = idx

  answers.value = await gameService.getAnswersForGameQuestion(targetId)
  // enrich answers with iTunes metadata when possible (spotify_id stores the external track id)
  await Promise.all(answers.value.map(async (a) => {
    try {
      if (a.spotify_id) {
        const res = await fetch(`https://itunes.apple.com/lookup?id=${encodeURIComponent(a.spotify_id)}`)
        if (res.ok) {
          const data = await res.json()
          if (data.results && data.results.length) {
            const s = data.results[0]
            a.artworkUrl60 = s.artworkUrl60
            a.trackName = s.trackName
            a.artistName = s.artistName
          }
        }
      }
    } catch (e) {
      console.debug('No metadata for answer', a.id, e)
    }
  }))
  guessesByAnswer.value = gameService.state.guesses[targetId] || {}

  // mirror guessCounts from service (may be updated by NEW_ANSWER handler)
  guessCountsState.value = gameService.state.guessCounts || {}

  // compute counts
  const map = {}
  Object.values(guessesByAnswer.value).forEach(arr => {
    arr.forEach(g => {
      const pid = g.guessed_player_id
      if (!pid) return
      map[pid] = (map[pid] || 0) + 1
    })
  })
  counts.value = map
}

onMounted(async () => {
  await load()
  // react to question changes
  watch(() => gameService.state.currentGameQuestionId, async (nid) => {
    await load(nid)
  })
  // react to guess updates so admin view updates live
  watch(() => JSON.stringify(gameService.state.guesses), async () => {
    const gqId = gameService.state.currentGameQuestionId || (gameQuestions.value[currentIndex.value] && gameQuestions.value[currentIndex.value].id)
    if (gqId) {
      guessesByAnswer.value = gameService.state.guesses[gqId] || {}
      // recompute counts
      const map = {}
      Object.values(guessesByAnswer.value).forEach(arr => {
        arr.forEach(g => {
          const pid = g.guessed_player_id
          if (!pid) return
          map[pid] = (map[pid] || 0) + 1
        })
      })
      counts.value = map
    }
  })
  // react to guessCounts updates coming from NEW_ANSWER parsing
  watch(() => JSON.stringify(gameService.state.guessCounts), async () => {
    const gqId = gameService.state.currentGameQuestionId || (gameQuestions.value[currentIndex.value] && gameQuestions.value[currentIndex.value].id)
    guessCountsState.value = gameService.state.guessCounts || {}
    // recompute aggregated counts (right column) using guessCounts if available
    if (gqId && guessCountsState.value[gqId]) {
      const agg = {}
      // guessCountsState[gqId] is { original_answer_id: { playerId: count } }
      Object.values(guessCountsState.value[gqId]).forEach(obj => {
        Object.entries(obj).forEach(([pid, c]) => {
          agg[pid] = (agg[pid] || 0) + c
        })
      })
      counts.value = agg
    }
  })
})

function applyCurrentQuestion() {
  const gq = gameQuestions.value[currentIndex.value]
  if (!gq) return
  // instruct all clients to change to this specific game question
  gameService.changeQuestion(currentIndex.value, { game_question_id: gq.id, game_question_text: gq.text })
}

function prev() {
  if (currentIndex.value > 0) {
    currentIndex.value -= 1
    applyCurrentQuestion()
  }
}

function next() {
  if (currentIndex.value < gameQuestions.value.length - 1) {
    currentIndex.value += 1
    applyCurrentQuestion()
  }
}
</script>

<style scoped>
.track-name { font-size: 1rem; font-weight: 500; }
.artist-name { font-size: 0.85rem; color: #cccccc; }
.card { max-width: 900px; margin: 0 auto; }

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
img {
  margin-right: 8px !important;
}
p {
  margin: 0 !important;
}
ul{
  list-style: none;
  margin: 0;
  padding: 0;
  width: 100%;
  max-width: none;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
  color: inherit;
  overflow: visible; /* allow parent/page scrolling instead of inner scroll */
  max-height: none;
}

.limited {
  /* When there are many answers, limit height and allow scrolling inside the column */
  max-height: 70vh;
  overflow-y: auto;
  padding: 0.75rem;
  background: rgba(0,0,0,0.06);
  border-radius: 0.75rem;
}

.track-name {
  font-size: 1rem;
  font-weight: 500;
}
.artist-name {
  font-size: 0.85rem;
  color: #cccccc;
}
.answer-item{
  transition: background-color 0.3s;
  margin-bottom: 20px;
  border-bottom: 2px solid red;
}

</style>
