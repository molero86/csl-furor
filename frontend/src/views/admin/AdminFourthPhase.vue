<template>
  <div class="min-screen flex-center py-8">
    <div class="w-full max-w-4xl px-6">

      <!-- Título -->
      <h1 class="text-5xl font-bold text-white text-center mb-12 animate-pulse-slow">
        🎰 Fase 4: Canta la canción 🎤
      </h1>

      <!-- Máquina Tragaperras -->
      <div v-if="!selectedSong && !spinning" class="slot-machine-container">
        <div class="slot-frame">
          <div class="slot-display empty-state">
            <div class="text-6xl mb-4">🎲</div>
            <p class="text-2xl text-white/80">¿Qué canción tocará?</p>
          </div>
        </div>
        
        <button
          class="button-comic text-2xl py-6 px-12 mt-8"
          @click="selectRandomSong"
          :disabled="loading || enrichedSongs.length === 0"
        >
          {{ loading ? 'Cargando canciones...' : '🎰 ¡Girar la Ruleta!' }}
        </button>
        
        <p v-if="enrichedSongs.length > 0" class="text-white/60 text-center mt-4">
          {{ enrichedSongs.length }} canciones disponibles
        </p>
      </div>

      <!-- Animación de la ruleta girando -->
      <div v-if="spinning" class="slot-machine-container">
        <div class="slot-frame spinning">
          <div class="slot-display">
            <div class="slot-reel">
              <div 
                v-for="(song, index) in displaySongs" 
                :key="index"
                class="slot-item"
              >
                <img 
                  v-if="song.artworkUrl100" 
                  :src="song.artworkUrl100" 
                  :alt="song.trackName"
                  class="album-cover"
                />
                <div v-else class="album-cover placeholder">
                  <span class="text-4xl">🎵</span>
                </div>
                <div class="song-info">
                  <p class="track-name">{{ song.trackName || song.text }}</p>
                  <p class="artist-name">{{ song.artistName || song.player_name }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <p class="text-white text-2xl text-center mt-8 animate-pulse">
          🎲 Girando la ruleta...
        </p>
      </div>

      <!-- Indicador de Buzzer Winner -->
      <div v-if="buzzerWinner && selectedSong && !spinning" class="buzzer-winner-card">
        <div class="winner-content">
          <div class="winner-icon">🏆</div>
          <h3 class="winner-title">¡Responde!</h3>
          <p class="winner-name">{{ buzzerWinner.player_name }}</p>
          <button
            class="button-comic reset-buzzer-button"
            @click="resetBuzzer"
          >
            🔄 Resetear Buzzer
          </button>
        </div>
      </div>

      <!-- Canción seleccionada (resultado final) -->
      <div v-if="selectedSong && !spinning" class="result-container">
        <!-- Flip Card Container (toda la tarjeta) -->
        <div class="flip-card-full" :class="{ flipped: flipped }">
          
          <!-- FRONT: Portada -->
          <div class="flip-card-front-full">
            <div class="result-card">
              <div class="confetti">🎉</div>
              <h2 class="text-4xl font-bold mb-6 text-white text-center">
                🎵 ¡Canción seleccionada! 🎵
              </h2>
              
              <div class="selected-song-display">
                <div class="album-cover-container" @click="playPreview">
                  <img 
                    v-if="selectedSong.artworkUrl100" 
                    :src="selectedSong.artworkUrl100" 
                    :alt="selectedSong.trackName"
                    class="result-album-cover"
                  />
                  <div v-else class="result-album-cover placeholder">
                    <span class="text-8xl">🎵</span>
                  </div>
                  <div v-if="selectedSong.previewUrl" class="play-overlay">
                    <div class="play-button">▶️</div>
                    <p class="play-text">Click para escuchar</p>
                  </div>
                </div>
                
                <button
                  class="button-comic flip-button"
                  @click="toggleFlip"
                >
                  📝 Ver Letra
                </button>
                
                <div class="result-info">
                  <p class="result-track-name">{{ selectedSong.trackName || selectedSong.text }}</p>
                  <p class="result-artist-name">{{ selectedSong.artistName || selectedSong.player_name }}</p>
                  <p class="result-player-name">Propuesta por: {{ selectedSong.player_name }}</p>
                </div>

                <!-- Reproductor de audio -->
                <audio 
                  v-if="selectedSong.previewUrl" 
                  ref="audioPlayer"
                  :src="selectedSong.previewUrl"
                  class="audio-player"
                  controls
                ></audio>
              </div>

              <div class="button-group">
                <button
                  class="button-comic text-2xl py-6 px-12 mt-8"
                  @click="nextQuestion"
                >
                  🎲 Siguiente Canción
                </button>
                
                <button
                  class="button-comic button-finish text-2xl py-6 px-12 mt-8"
                  @click="finishPhase"
                >
                  🏁 Finalizar Fase
                </button>
              </div>
            </div>
          </div>

          <!-- BACK: Letra -->
          <div class="flip-card-back-full">
            <div class="result-card">
              <h2 class="text-4xl font-bold mb-6 text-white text-center">
                📝 Letra de la canción
              </h2>
              
              <div class="selected-song-display">
                <div class="lyrics-container-full">
                  <div v-if="loadingLyrics" class="lyrics-loading">
                    <div class="text-6xl mb-4">⏳</div>
                    <p class="text-xl">Cargando letra...</p>
                  </div>
                  <div v-else class="lyrics-content-full">
                    <pre class="lyrics-text-full">{{ lyrics }}</pre>
                  </div>
                </div>
                
                <button
                  class="button-comic flip-button"
                  @click="toggleFlip"
                >
                  🔙 Ver Portada
                </button>
                
                <div class="result-info mt-4">
                  <p class="result-track-name">{{ selectedSong.trackName || selectedSong.text }}</p>
                  <p class="result-artist-name">{{ selectedSong.artistName || selectedSong.player_name }}</p>
                </div>
              </div>

              <div class="button-group">
                <button
                  class="button-comic text-2xl py-6 px-12 mt-8"
                  @click="nextQuestion"
                >
                  🎲 Siguiente Canción
                </button>
                
                <button
                  class="button-comic button-finish text-2xl py-6 px-12 mt-8"
                  @click="finishPhase"
                >
                  🏁 Finalizar Fase
                </button>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- Formulario de puntuación -->
      <div v-if="selectedSong && !spinning" class="scoring-form">
        <div class="form-card">
          <h3 class="text-2xl font-bold text-white mb-4 text-center">
            🏆 Asignar Puntos
          </h3>
          
          <div class="form-content">
            <div class="form-group">
              <label for="playerSelect" class="form-label">Jugador:</label>
              <select 
                id="playerSelect" 
                v-model="selectedPlayerId"
                class="form-select"
              >
                <option value="" disabled>Selecciona un jugador</option>
                <option 
                  v-for="player in players" 
                  :key="player.id" 
                  :value="player.id"
                >
                  {{ player.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="pointsInput" class="form-label">Puntos:</label>
              <input 
                id="pointsInput"
                v-model.number="points"
                type="number"
                min="0"
                max="100"
                class="form-input"
                placeholder="0"
              />
            </div>
            
            <button
              class="button-comic submit-button"
              @click="submitPoints"
              :disabled="!selectedPlayerId || points === null || submittingPoints"
            >
              {{ submittingPoints ? '⏳ Guardando...' : '✅ Sumar Puntos' }}
            </button>
          </div>
          
          <div v-if="pointsMessage" class="points-message" :class="pointsMessageType">
            {{ pointsMessage }}
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import gameService from '../../services/gameService'

const loading = ref(false)
const selectedSong = ref(null)
const availableSongs = ref([])
const enrichedSongs = ref([])
const spinning = ref(false)
const displaySongs = ref([])
const flipped = ref(false)
const lyrics = ref('')
const loadingLyrics = ref(false)

// Estado del buzzer
const buzzerWinner = computed(() => gameService.state.buzzerWinner)

// Variables para el formulario de puntos
const players = ref([])
const selectedPlayerId = ref('')
const points = ref(null)
const submittingPoints = ref(false)
const pointsMessage = ref('')
const pointsMessageType = ref('success')
const currentGameQuestionId = ref(null)

onMounted(async () => {
  await loadSongs()
  await loadPlayers()
  await loadCurrentGameQuestion()
})

// Watch para mostrar notificación cuando alguien presiona el buzzer
watch(buzzerWinner, (newWinner) => {
  if (newWinner) {
    console.log('🏆 Ganador del buzzer:', newWinner.player_name)
  }
})

async function loadSongs() {
  loading.value = true
  try {
    availableSongs.value = await gameService.getPhase1Songs()
    console.log('🎵 Canciones disponibles:', availableSongs.value.length)
    
    // Enriquecer canciones con datos de iTunes
    await enrichSongsWithItunes()
  } catch (error) {
    console.error('❌ Error cargando canciones:', error)
    alert('Error al cargar las canciones')
  } finally {
    loading.value = false
  }
}

async function enrichSongsWithItunes() {
  const enriched = []
  
  for (const song of availableSongs.value) {
    try {
      // Buscar en iTunes usando el texto de la canción
      const res = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(song.text)}&entity=song&limit=1`)
      const data = await res.json()
      
      if (data.results && data.results.length > 0) {
        const itunesData = data.results[0]
        enriched.push({
          ...song,
          artworkUrl100: itunesData.artworkUrl100,
          artworkUrl60: itunesData.artworkUrl60,
          trackName: itunesData.trackName,
          artistName: itunesData.artistName,
          previewUrl: itunesData.previewUrl
        })
      } else {
        // Si no se encuentra en iTunes, usar datos por defecto
        enriched.push({
          ...song,
          artworkUrl100: null,
          trackName: song.text,
          artistName: song.player_name,
          previewUrl: null
        })
      }
    } catch (error) {
      console.error('Error enriqueciendo canción:', error)
      enriched.push({
        ...song,
        artworkUrl100: null,
        trackName: song.text,
        artistName: song.player_name,
        previewUrl: null
      })
    }
  }
  
  enrichedSongs.value = enriched
  console.log('✨ Canciones enriquecidas:', enrichedSongs.value.length)
}

async function selectRandomSong() {
  if (enrichedSongs.value.length === 0) {
    alert('No hay canciones disponibles')
    return
  }

  spinning.value = true
  
  // Crear array de canciones para mostrar en el slot (repetidas para efecto continuo)
  const songsForSlot = [...enrichedSongs.value, ...enrichedSongs.value, ...enrichedSongs.value]
  displaySongs.value = songsForSlot
  
  // Elegir una canción aleatoria del array original
  const randomIndex = Math.floor(Math.random() * enrichedSongs.value.length)
  const chosenSong = enrichedSongs.value[randomIndex]
  
  // Esperar a que termine la animación (3 segundos)
  setTimeout(() => {
    spinning.value = false
    selectedSong.value = chosenSong
    console.log('🎲 Canción elegida:', selectedSong.value)
    
    // Cargar la letra en background
    fetchLyrics()
    
    // Remover la canción seleccionada de las disponibles
    const indexInEnriched = enrichedSongs.value.findIndex(s => s.spotify_id === chosenSong.spotify_id)
    if (indexInEnriched > -1) {
      enrichedSongs.value.splice(indexInEnriched, 1)
    }
  }, 3500)
}

function nextQuestion() {
  // Detener el audio si está reproduciéndose
  const audio = document.querySelector('audio')
  if (audio) {
    audio.pause()
    audio.currentTime = 0
  }
  
  // Resetear estados
  flipped.value = false
  lyrics.value = ''
  
  // Resetear el buzzer para la siguiente canción
  gameService.resetBuzzer()
  
  // Resetear la canción seleccionada para poder elegir otra
  selectedSong.value = null
  displaySongs.value = []
}

function resetBuzzer() {
  console.log('🔄 Reseteando buzzer manualmente')
  gameService.resetBuzzer()
}

function finishPhase() {
  const gameCode = gameService.state.game?.code
  if (!gameCode) {
    console.error('❌ No hay código de juego disponible')
    return
  }
  
  // Notificar a todos los clientes (incluido el admin) que deben navegar a final-scores
  // El servidor hará broadcast y todos navegarán automáticamente via handle_SHOW_FINAL_SCORES
  gameService.showFinalScores()
}

function playPreview() {
  if (!selectedSong.value?.previewUrl) return
  
  const audio = document.querySelector('audio')
  if (audio) {
    if (audio.paused) {
      audio.play()
      console.log('▶️ Reproduciendo preview...')
    } else {
      audio.pause()
      console.log('⏸️ Pausado')
    }
  }
}

function toggleFlip() {
  console.log('🔄 Toggle flip - Estado actual:', flipped.value)
  flipped.value = !flipped.value
  console.log('✅ Nuevo estado flip:', flipped.value)
  
  if (lyrics.value) {
    console.log('📄 Letra disponible:', lyrics.value.substring(0, 100) + '...')
  } else if (loadingLyrics.value) {
    console.log('⏳ Letra aún cargando...')
  } else {
    console.log('❌ No hay letra disponible')
  }
}

async function fetchLyrics() {
  if (!selectedSong.value) return
  
  loadingLyrics.value = true
  try {
    const artist = selectedSong.value.artistName || selectedSong.value.player_name
    const track = selectedSong.value.trackName || selectedSong.value.text
    
    console.log('🔍 Buscando letra para:', artist, '-', track)
    
    // Intentar con múltiples APIs en orden
    const apis = [
      // API 1: lrclib.net (especializada en letras)
      async () => {
        try {
          const cleanTrack = track.split('-')[0].trim()
          const cleanArtist = artist.trim()
          
          const response = await fetch(
            `https://lrclib.net/api/search?artist_name=${encodeURIComponent(cleanArtist)}&track_name=${encodeURIComponent(cleanTrack)}`,
            { signal: AbortSignal.timeout(5000) }
          )
          if (response.ok) {
            const data = await response.json()
            if (data && data.length > 0 && data[0].plainLyrics) {
              console.log('✅ Letra encontrada en lrclib.net')
              return data[0].plainLyrics
            }
          }
        } catch (e) {
          console.log('API lrclib.net falló:', e.message)
        }
        return null
      },
      
      // API 2: lyrics.ovh
      async () => {
        try {
          const response = await fetch(
            `https://api.lyrics.ovh/v1/${encodeURIComponent(artist)}/${encodeURIComponent(track)}`,
            { signal: AbortSignal.timeout(5000) }
          )
          if (response.ok) {
            const data = await response.json()
            if (data.lyrics) {
              console.log('✅ Letra encontrada en lyrics.ovh')
              return data.lyrics
            }
          }
        } catch (e) {
          console.log('API lyrics.ovh falló:', e.message)
        }
        return null
      },
      
      // API 3: some-random-api.com
      async () => {
        try {
          const cleanTrack = track.split('-')[0].trim()
          const cleanArtist = artist.trim()
          
          const response = await fetch(
            `https://some-random-api.com/others/lyrics?title=${encodeURIComponent(cleanTrack + ' ' + cleanArtist)}`,
            { signal: AbortSignal.timeout(5000) }
          )
          if (response.ok) {
            const data = await response.json()
            if (data.lyrics) {
              console.log('✅ Letra encontrada en some-random-api.com')
              return data.lyrics
            }
          }
        } catch (e) {
          console.log('API some-random-api.com falló:', e.message)
        }
        return null
      }
    ]
    
    // Intentar cada API hasta que una funcione
    for (const apiCall of apis) {
      try {
        const result = await apiCall()
        if (result) {
          lyrics.value = result
          console.log('📝 Letra cargada correctamente')
          return
        }
      } catch (error) {
        console.log('Intento de API falló:', error.message)
        continue
      }
    }
    
    // Si ninguna API funcionó, mostrar mensaje informativo
    lyrics.value = `No se encontró la letra para esta canción.\n\n🎤 Puedes cantarla sin letra y comprobar quién la canta mejor!\n\nCanción: ${track}\nArtista: ${artist}`
    console.log('❌ No se pudo encontrar la letra en ninguna API')
    
  } catch (error) {
    console.error('❌ Error obteniendo letra:', error)
    lyrics.value = `Error al buscar la letra.\n\n🎤 ¡No pasa nada! Pueden cantar la canción sin letra.\n\nCanción: ${selectedSong.value.trackName || selectedSong.value.text}`
  } finally {
    loadingLyrics.value = false
    console.log('✅ fetchLyrics completado')
  }
}

async function loadPlayers() {
  try {
    players.value = gameService.getPlayers()
    console.log('👥 Jugadores cargados:', players.value.length)
  } catch (error) {
    console.error('❌ Error cargando jugadores:', error)
  }
}

async function loadCurrentGameQuestion() {
  try {
    // Obtener las game_questions de fase 4
    let phase4Questions = await gameService.getQuestionsForPhase(4)
    
    // Si no existen preguntas de fase 4, generarlas automáticamente
    if (!phase4Questions || phase4Questions.length === 0) {
      console.log('⚠️ No hay game_questions para fase 4, generando...')
      await generatePhase4Questions()
      // Volver a cargar después de generar
      phase4Questions = await gameService.getQuestionsForPhase(4)
    }
    
    if (phase4Questions && phase4Questions.length > 0) {
      // Usar la primera pregunta de fase 4 para guardar las respuestas
      currentGameQuestionId.value = phase4Questions[0].id
      console.log('📝 Game Question ID para Fase 4:', currentGameQuestionId.value)
    } else {
      console.warn('⚠️ No se pudieron cargar o generar game_questions para fase 4')
    }
  } catch (error) {
    console.error('❌ Error cargando game_question:', error)
  }
}

async function generatePhase4Questions() {
  try {
    const API_URL = import.meta.env.VITE_API_URL
    const gameCode = gameService.state.game?.code
    
    if (!gameCode) {
      console.error('❌ No hay código de juego disponible')
      return
    }
    
    // Paso 1: Inicializar preguntas base de Fase 4 (en la tabla questions)
    console.log('📚 Inicializando preguntas base de Fase 4...')
    const initResponse = await fetch(`${API_URL}/questions/initialize-phase/4`, {
      method: 'POST'
    })
    
    if (!initResponse.ok) {
      console.error('❌ Error inicializando preguntas base de Fase 4')
      return
    }
    
    const initData = await initResponse.json()
    console.log('✅ Preguntas base:', initData)
    
    // Paso 2: Generar game_questions para esta partida
    console.log('🔨 Generando game_questions de Fase 4 para la partida...')
    const response = await fetch(`${API_URL}/games/${gameCode}/generate-phase/4`, {
      method: 'POST'
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      console.error('❌ Error generando fase 4:', errorData)
      return
    }
    
    const data = await response.json()
    console.log('✅ Game questions de Fase 4 generadas:', data)
  } catch (error) {
    console.error('❌ Error en generatePhase4Questions:', error)
  }
}

async function submitPoints() {
  if (!selectedPlayerId.value || points.value === null) {
    pointsMessage.value = '⚠️ Selecciona un jugador y una puntuación'
    pointsMessageType.value = 'error'
    return
  }
  
  if (!currentGameQuestionId.value) {
    pointsMessage.value = '❌ No se encontró la pregunta de la fase 4'
    pointsMessageType.value = 'error'
    return
  }
  
  submittingPoints.value = true
  pointsMessage.value = ''
  
  try {
    const API_URL = import.meta.env.VITE_API_URL
    const response = await fetch(`${API_URL}/answers`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        player_id: selectedPlayerId.value,
        game_question_id: currentGameQuestionId.value,
        text: `Puntos por cantar: ${selectedSong.value.trackName || selectedSong.value.text}`,
        correct: points.value,
        spotify_id: selectedSong.value.spotify_id || null
      })
    })
    
    if (!response.ok) {
      throw new Error('Error al guardar los puntos')
    }
    
    const player = players.value.find(p => p.id === selectedPlayerId.value)
    pointsMessage.value = `✅ ${points.value} puntos asignados a ${player?.name || 'el jugador'}`
    pointsMessageType.value = 'success'
    
    // Resetear formulario
    selectedPlayerId.value = ''
    points.value = null
    
    // Limpiar mensaje después de 3 segundos
    setTimeout(() => {
      pointsMessage.value = ''
    }, 3000)
    
    console.log('✅ Puntos guardados correctamente')
  } catch (error) {
    console.error('❌ Error guardando puntos:', error)
    pointsMessage.value = '❌ Error al guardar los puntos'
    pointsMessageType.value = 'error'
  } finally {
    submittingPoints.value = false
  }
}
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

.slot-machine-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.slot-frame {
  position: relative;
  width: 100%;
  max-width: 600px;
  height: 400px;
  background: linear-gradient(145deg, #1e293b, #0f172a);
  border-radius: 2rem;
  padding: 2rem;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.5),
    inset 0 0 20px rgba(255, 215, 0, 0.1);
  border: 4px solid #fbbf24;
  overflow: hidden;
}

.slot-frame.spinning {
  animation: shake 0.5s infinite;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px) rotate(-0.5deg); }
  75% { transform: translateX(5px) rotate(0.5deg); }
}

.slot-display {
  position: relative;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 1rem;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.slot-display.empty-state {
  flex-direction: column;
}

.slot-reel {
  display: flex;
  flex-direction: column;
  animation: spin 3.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  animation-fill-mode: forwards;
}

@keyframes spin {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-80%);
  }
}

.slot-item {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
  min-height: 140px;
}

.album-cover {
  width: 100px;
  height: 100px;
  border-radius: 0.75rem;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  flex-shrink: 0;
}

.album-cover.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.song-info {
  flex: 1;
  text-align: left;
}

.track-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.artist-name {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
}

.result-container {
  display: flex;
  justify-content: center;
  width: 100%;
}

.result-card {
  width: 100%;
  max-width: 700px;
  background: linear-gradient(145deg, rgba(251, 191, 36, 0.15), rgba(255, 255, 255, 0.05));
  border: 3px solid #fbbf24;
  border-radius: 2rem;
  padding: 3rem;
  box-shadow: 0 20px 60px rgba(251, 191, 36, 0.3);
  position: relative;
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.confetti {
  position: absolute;
  top: -20px;
  right: -20px;
  font-size: 4rem;
  animation: bounce 1s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(10deg); }
}

.selected-song-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
}

/* Flip Card Container - Toda la tarjeta */
.flip-card-full {
  position: relative;
  width: 100%;
  max-width: 700px;
  perspective: 2000px;
  transform-style: preserve-3d;
}

.flip-card-full.flipped .flip-card-front-full {
  transform: rotateY(180deg);
}

.flip-card-full.flipped .flip-card-back-full {
  transform: rotateY(0deg);
}

.flip-card-front-full,
.flip-card-back-full {
  position: absolute;
  width: 100%;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  transition: transform 1s cubic-bezier(0.4, 0.0, 0.2, 1);
  transform-style: preserve-3d;
}

.flip-card-front-full {
  transform: rotateY(0deg);
  position: relative;
}

.flip-card-back-full {
  transform: rotateY(180deg);
  position: absolute;
  top: 0;
  left: 0;
}

.lyrics-container-full {
  width: 100%;
  min-height: 400px;
  max-height: 500px;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 1.5rem;
  overflow-y: auto;
  margin: 2rem 0;
}

.lyrics-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  color: white;
}

.lyrics-content-full {
  width: 100%;
  display: flex;
  flex-direction: column;
}

.lyrics-text-full {
  font-size: 1rem;
  line-height: 1.6;
  color: white;
  white-space: pre-wrap;
  font-family: 'Georgia', serif;
  text-align: left;
  padding: 1rem;
  margin: 0;
}

.lyrics-container-full::-webkit-scrollbar {
  width: 8px;
}

.lyrics-container-full::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.lyrics-container-full::-webkit-scrollbar-thumb {
  background: rgba(251, 191, 36, 0.5);
  border-radius: 4px;
}

.lyrics-container-full::-webkit-scrollbar-thumb:hover {
  background: rgba(251, 191, 36, 0.7);
}

.flip-button {
  padding: 1rem 2rem !important;
  font-size: 1.25rem !important;
}

.album-cover-container {
  position: relative;
  cursor: pointer;
  width: 250px;
  height: 250px;
  transition: transform 0.3s ease;
}

.album-cover-container:hover {
  transform: scale(1.05);
}

.album-cover-container:hover .play-overlay {
  opacity: 1;
}

.result-album-cover {
  width: 100%;
  height: 100%;
  border-radius: 1.5rem;
  object-fit: cover;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  border: 4px solid rgba(255, 255, 255, 0.2);
  animation: pulse 2s ease-in-out infinite;
}

.play-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.play-button {
  font-size: 4rem;
  margin-bottom: 0.5rem;
  animation: pulse-play 1.5s ease-in-out infinite;
}

@keyframes pulse-play {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.play-text {
  color: white;
  font-size: 1.25rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.result-album-cover.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.result-info {
  text-align: center;
  width: 100%;
}

.result-track-name {
  font-size: 2.5rem;
  font-weight: 900;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  line-height: 1.2;
}

.result-artist-name {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1rem;
  font-weight: 600;
}

.result-player-name {
  font-size: 1.25rem;
  color: #fbbf24;
  font-weight: 700;
  padding: 0.75rem 1.5rem;
  background: rgba(251, 191, 36, 0.1);
  border-radius: 1rem;
  display: inline-block;
  margin-top: 1rem;
}

.button-comic:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  width: 100%;
}

.button-finish {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
  border-color: #10b981 !important;
}

.button-finish:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
  transform: translateY(-2px) scale(1.05);
}

.audio-player {
  width: 100%;
  max-width: 400px;
  margin-top: 1rem;
  border-radius: 2rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem;
}

.audio-player::-webkit-media-controls-panel {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.2), rgba(255, 255, 255, 0.1));
  border-radius: 1.5rem;
}

.audio-player::-webkit-media-controls-play-button,
.audio-player::-webkit-media-controls-pause-button {
  background-color: #fbbf24;
  border-radius: 50%;
}

/* Formulario de puntuación */
.scoring-form {
  margin-top: 3rem;
  display: flex;
  justify-content: center;
  width: 100%;
}

.form-card {
  width: 100%;
  max-width: 500px;
  background: linear-gradient(145deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
  border: 3px solid #818cf8;
  border-radius: 1.5rem;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 1.125rem;
  font-weight: 600;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.form-select,
.form-input {
  width: 100%;
  padding: 0.875rem 1rem;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.75rem;
  color: white;
  transition: all 0.3s ease;
  font-weight: 500;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #fbbf24;
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.1);
}

.form-select option {
  background: #1e293b;
  color: white;
  padding: 0.5rem;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.submit-button {
  margin-top: 0.5rem;
  width: 100%;
  padding: 1rem 2rem !important;
  font-size: 1.25rem !important;
  font-weight: 700 !important;
}

.submit-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.points-message {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  font-weight: 600;
  text-align: center;
  animation: slideIn 0.3s ease-out;
}

.points-message.success {
  background: rgba(34, 197, 94, 0.2);
  border: 2px solid #22c55e;
  color: #86efac;
}

.points-message.error {
  background: rgba(239, 68, 68, 0.2);
  border: 2px solid #ef4444;
  color: #fca5a5;
}

/* Buzzer Winner Card */
.buzzer-winner-card {
  width: 100%;
  max-width: 500px;
  background: linear-gradient(145deg, rgba(251, 191, 36, 0.2), rgba(245, 158, 11, 0.1));
  border: 4px solid #fbbf24;
  border-radius: 2rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 20px 60px rgba(251, 191, 36, 0.5);
  animation: slideIn 0.5s ease-out, pulse 2s ease-in-out infinite;
}

.winner-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.winner-icon {
  font-size: 5rem;
  animation: bounce 1s ease-in-out infinite;
}

.winner-title {
  font-size: 2rem;
  font-weight: 900;
  color: white;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.winner-name {
  font-size: 3rem;
  font-weight: 900;
  color: #fbbf24;
  text-shadow: 
    0 4px 8px rgba(0, 0, 0, 0.5),
    0 0 20px rgba(251, 191, 36, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.reset-buzzer-button {
  margin-top: 1rem;
  padding: 0.75rem 2rem !important;
  font-size: 1.125rem !important;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
  border-color: #3b82f6 !important;
}

.reset-buzzer-button:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
}
</style>
