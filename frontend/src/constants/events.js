// src/constants/events.js

// Eventos enviados por el cliente → servidor
export const CLIENT_EVENTS = {
  JOIN_GAME: 'join_game',
  LEAVE_GAME: 'leave_game',
  SEND_ANSWER: 'send_answer',
  REQUEST_UPDATE: 'request_update', // pedir estado actual de la partida
}

// Eventos enviados por el servidor → cliente
export const SERVER_EVENTS = {
  PLAYER_JOINED: 'player_joined',
  PLAYER_LEFT: 'player_left',
  GAME_UPDATED: 'game_updated',
  NEW_ANSWER: 'new_answer',
  ERROR: 'error',
}
