const API_URL = (typeof window !== 'undefined' && window.__env && window.__env.VITE_API_URL) || import.meta.env.VITE_API_URL;

export async function createGame() {
  const response = await fetch(`${API_URL}/games`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) throw new Error("Error al crear la partida");
  return response.json();
}

export async function getGame(gameCode) {
  const response = await fetch(`${API_URL}/games/${gameCode}`);

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error("Error al obtener la partida");
  }

  return await response.json();
}

export async function getPlayers(gameId) {
  const response = await fetch(`${API_URL}/games/${gameId}/players`);
  if (!response.ok) throw new Error("Error al obtener jugadores");
  return response.json();
}

export async function addPlayer(gameId, playerName) {
  const response = await fetch(`${API_URL}/games/${gameId}/players`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: playerName }),
  });
  if (!response.ok) throw new Error("Error al añadir jugador");
  return response.json();
}
