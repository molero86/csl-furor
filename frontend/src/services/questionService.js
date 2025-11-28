const API_URL = import.meta.env.VITE_API_URL;

export async function getQuestions() {
  const res = await fetch(`${API_URL}/questions`);
  if (!res.ok) throw new Error('Error al obtener preguntas');
  return res.json();
}

export async function getQuestion(id) {
  const res = await fetch(`${API_URL}/questions/${id}`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error('Error al obtener la pregunta');
  return res.json();
}

export async function createQuestion(payload) {
  const res = await fetch(`${API_URL}/questions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Error al crear la pregunta');
  return res.json();
}

export async function updateQuestion(id, payload) {
  const res = await fetch(`${API_URL}/questions/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Error al actualizar la pregunta');
  return res.json();
}

export async function deleteQuestion(id) {
  const res = await fetch(`${API_URL}/questions/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Error al borrar la pregunta');
  return res.json();
}

export default {
  getQuestions,
  getQuestion,
  createQuestion,
  updateQuestion,
  deleteQuestion,
};