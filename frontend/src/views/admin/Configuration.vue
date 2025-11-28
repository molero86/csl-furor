<template>
  <div class="min-screen flex-center">
    <div class="card w-full max-w-3xl p-6">
      <h1 class="text-2xl font-bold mb-4">Configuración de Preguntas</h1>

      <!-- Formulario Crear/Editar -->
      <div class="mb-6">
        <h2 class="font-semibold mb-2">{{ editing.id ? 'Editar pregunta' : 'Crear nueva pregunta' }}</h2>
        <div class="grid grid-cols-3 gap-3 items-end">
          <div>
            <label class="text-sm text-white block">Fase</label>
            <input v-model.number="editing.phase" type="number" min="1" class="input-comic w-full" />
          </div>
          <div>
            <label class="text-sm text-white block">Orden</label>
            <input v-model.number="editing.order" type="number" min="1" class="input-comic w-full" />
          </div>
          <div>
            <label class="text-sm text-white block">Tipo</label>
            <input v-model="editing.type" class="input-comic w-full" />
          </div>
          <div class="col-span-3">
            <label class="text-sm text-white block">Texto</label>
            <input v-model="editing.text" class="input-comic w-full" />
          </div>
        </div>
        <div class="mt-3 flex gap-2">
          <button class="button-comic" @click="saveQuestion">{{ editing.id ? 'Guardar' : 'Crear' }}</button>
          <button class="button-comic bg-gray-600" @click="resetForm">Cancelar</button>
        </div>
      </div>

      <!-- Lista de preguntas -->
      <div>
        <h2 class="font-semibold mb-2">Preguntas base</h2>
        <table class="w-full table-auto text-left">
          <thead>
            <tr>
              <th class="px-2">ID</th>
              <th class="px-2">Fase</th>
              <th class="px-2">Orden</th>
              <th class="px-2">Tipo</th>
              <th class="px-2">Texto</th>
              <th class="px-2">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="q in questions" :key="q.id" class="odd:bg-slate-800/50">
              <td class="px-2 py-2">{{ q.id }}</td>
              <td class="px-2 py-2">{{ q.phase }}</td>
              <td class="px-2 py-2">{{ q.order }}</td>
              <td class="px-2 py-2">{{ q.type }}</td>
              <td class="px-2 py-2">{{ q.text }}</td>
              <td class="px-2 py-2">
                <div class="flex gap-2">
                  <button class="button-comic px-2 py-1" @click="editQuestion(q)">Editar</button>
                  <button class="button-comic bg-red-600 px-2 py-1" @click="removeQuestion(q)">Borrar</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as questionService from '../../services/questionService'

const questions = ref([])

const empty = { id: null, phase: 1, order: 1, text: '', type: 'text' }
const editing = ref({ ...empty })

async function load() {
  try {
    const data = await questionService.getQuestions()
    questions.value = data
  } catch (err) {
    console.error(err)
    alert(err.message || 'Error cargando preguntas')
  }
}

function editQuestion(q) {
  editing.value = { ...q }
}

function resetForm() {
  editing.value = { ...empty }
}

async function saveQuestion() {
  try {
    if (editing.value.id) {
      const updated = await questionService.updateQuestion(editing.value.id, {
        phase: editing.value.phase,
        order: editing.value.order,
        text: editing.value.text,
        type: editing.value.type,
      })
      // replace in list
      const idx = questions.value.findIndex(x => x.id === updated.id)
      if (idx !== -1) questions.value.splice(idx, 1, updated)
    } else {
      const created = await questionService.createQuestion({
        phase: editing.value.phase,
        order: editing.value.order,
        text: editing.value.text,
        type: editing.value.type,
      })
      questions.value.push(created)
    }
    resetForm()
  } catch (err) {
    console.error(err)
    alert(err.message || 'Error saving question')
  }
}

async function removeQuestion(q) {
  if (!confirm('Borrar pregunta #' + q.id + '?')) return
  try {
    await questionService.deleteQuestion(q.id)
    const idx = questions.value.findIndex(x => x.id === q.id)
    if (idx !== -1) questions.value.splice(idx, 1)
  } catch (err) {
    console.error(err)
    alert(err.message || 'Error borrando pregunta')
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
/* Estilos mínimos, la app ya tiene utilidades */
</style>
