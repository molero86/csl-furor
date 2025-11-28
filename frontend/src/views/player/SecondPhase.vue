<template>
  <div class="min-screen flex-center bg-spotify-gradient px-4 overflow-hidden relative">
    
    <!-- Intro inicial -->
    <transition name="fade">
      <div v-if="showIntro" class="absolute bottom-8 w-full text-center text-white/70 waiting-text">
        <h1>Fase 2. ¿Quien respondió qué?</h1>
      </div>

      <!-- Pantalla principal -->
      <div v-else class="flex flex-col justify-between items-center w-full h-full py-10 text-white">
        
        <!-- Pregunta -->
        <div class="text-center mt-10 w-full max-w-md">
          <h2 class="text-2xl font-bold mb-6">{{ question }}</h2>

          <!-- Campo de texto -->
          <input
            v-model="query"
            @input="debouncedSearch"
            type="text"
            placeholder="Busca una canción..."
            class="input-comic w-full text-center"
          />

          <!-- Resultados -->
          <ul v-if="songs.length" class="mt-4 bg-white/10 rounded-2xl p-2 divide-y divide-white/20">
            <li
              v-for="song in songs"
              :key="song.trackId"
              class="flex items-center gap-3 p-2 hover:bg-white/20 cursor-pointer rounded-xl"
              @click="selectSong(song)"
            >
              <img :src="song.artworkUrl60" class="w-10 h-10 rounded-lg" alt="cover" />
              <div class="text-left">
                <p class="font-semibold text-sm track-name">{{ song.trackName }}</p>
                <p class="text-xs text-white/70 artist-name">{{ song.artistName }}</p>
              </div>
            </li>
          </ul>

          <!-- Canción seleccionada -->
          <ul v-if="selectedSong" class="mt-4 bg-white/10 rounded-2xl p-2 divide-y divide-white/20">
            <li class="flex items-center gap-3 p-2 hover:bg-white/20 cursor-pointer rounded-xl">
              <img :src="selectedSong.artworkUrl60" class="w-10 h-10 rounded-lg" alt="cover" />
              <div class="text-left">
                <p class="font-semibold text-sm track-name">{{ selectedSong.trackName }}</p>
                <p class="text-xs text-white/70 artist-name">{{ selectedSong.artistName }}</p>
              </div>
            </li>
          </ul>

        </div>

        <!-- Botón Enviar -->
        <button
          class="button-comic px-6 py-2 mt-auto mb-10"
          @click="submitAnswer"
          :disabled="!selectedSong"
        >
          Enviar
        </button>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import gameService from '../../services/gameService'

const showIntro = ref(true)
let currentPhaseQuestion = ref("")
const query = ref("")
const songs = ref([])
const selectedSong = ref(null)
let searchTimeout = null

async function searchSongs() {
  if (!query.value.trim()) {
    songs.value = []
    return
  }

  const res = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(query.value)}&entity=song&limit=5`)
  const data = await res.json()
  songs.value = data.results
}

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(searchSongs, 500) // Espera 0.5s tras dejar de escribir
}

function selectSong(song) {
  selectedSong.value = song
  query.value = `${song.trackName} - ${song.artistName}`
  songs.value = [] // Ocultar resultados tras seleccionar
}

function submitAnswer() {
  console.log("🎵 Canción seleccionada:", selectedSong.value)
  alert(`Has elegido: ${selectedSong.value.trackName} - ${selectedSong.value.artistName}`)
}

onMounted(() => {
  //Check each second what is the current question
  setInterval(async () => {
    const question = await gameService.getCurrentPhaseQuestion()
    console.log("Pregunta actual:", question)
    if (question) {
      currentPhaseQuestion.value = question.text
    }
  }, 1000)

  setTimeout(() => {
    showIntro.value = false
  }, 3000)
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
img {
  margin-right: 8px !important;
}
p {
  margin: 0 !important;
}
ul{
  list-style: none;
  margin: 1rem;
  padding: 1rem;
  width: 85%;
  max-width: 500px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 1rem;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
  color: white;
  overflow-y: auto;
  max-height: 300px;
}

.track-name {
  font-size: 1rem;
  font-weight: 500;
}
.artist-name {
  font-size: 0.85rem;
  color: #cccccc;
}

</style>
