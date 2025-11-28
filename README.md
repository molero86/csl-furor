# 🎵 Diagrama funcional de eventos WebSocket – Canciones Furor

## 🧩 Participantes
- **Server**: gestiona el estado global del juego (jugadores, fases, preguntas, puntuaciones, etc.).
- **Administrator**: controla el flujo del juego (inicia partidas, cambia fases, cambia preguntas).
- **Player**: interactúa respondiendo preguntas y participando en las fases.

---

## 🧑‍💻 PLAYER

### 🔹 Emite
| Evento | Payload | Descripción |
|---------|----------|--------------|
| `JOIN_PLAYER` | `{ gameId, playerName }` | Solicita unirse a una partida existente. |
| `ADD_ANSWER` | `{ gameId, playerId, questionId, answer }` | Envía una respuesta a la pregunta actual. |

### 🔹 Recibe
| Evento | Acción al recibirlo |
|---------|--------------------|
| `PLAYER_JOINED` | Actualiza la lista de jugadores en pantalla. |
| `GAME_STARTED` | Cambia la vista a la primera fase del juego. |
| `PHASE_CHANGED` | Actualiza la UI para mostrar la nueva fase. |
| `QUESTION_CHANGED` | Muestra la nueva pregunta o letra a completar. |

---

## 👑 ADMINISTRATOR

### 🔹 Emite
| Evento | Payload | Descripción |
|---------|----------|--------------|
| `START_GAME` | `{ gameId }` | Inicia la partida. |
| `CHANGE_PHASE` | `{ gameId, newPhase }` | Avanza a la siguiente fase del juego. |
| `CHANGE_QUESTION` | `{ gameId, newQuestion }` | Cambia la pregunta actual dentro de una fase. |

### 🔹 Recibe
| Evento | Acción al recibirlo |
|---------|--------------------|
| `PLAYER_JOINED` | Actualiza el panel de control con el nuevo jugador. |
| `ADD_ANSWER` | Muestra las respuestas enviadas por los jugadores (para validación o revisión). |
| `PHASE_CHANGED` | Sincroniza la vista con los jugadores. |
| `QUESTION_CHANGED` | Actualiza la vista de la pregunta actual. |

---

## 🧠 SERVER

### 🔹 Recibe
| Evento | Origen | Acción |
|---------|---------|--------|
| `JOIN_PLAYER` | Player | Añade el jugador al listado y emite `PLAYER_JOINED` a todos. |
| `ADD_ANSWER` | Player | Registra la respuesta en la partida. |
| `START_GAME` | Administrator | Cambia el estado de la partida a “en curso” y emite `GAME_STARTED`. |
| `CHANGE_PHASE` | Administrator | Actualiza la fase actual y emite `PHASE_CHANGED`. |
| `CHANGE_QUESTION` | Administrator | Actualiza la pregunta actual y emite `QUESTION_CHANGED`. |

### 🔹 Emite
| Evento | Destinatarios | Descripción |
|---------|----------------|--------------|
| `PLAYER_JOINED` | Todos los jugadores y administrador | Notifica que un nuevo jugador se ha unido. |
| `GAME_STARTED` | Todos | Señal de inicio de la partida. |
| `PHASE_CHANGED` | Todos | Indica el cambio de fase. |
| `QUESTION_CHANGED` | Todos | Indica que hay una nueva pregunta o letra. |

---

## 🔁 Flujo general de eventos

```mermaid
sequenceDiagram
    participant Player
    participant Administrator
    participant Server

    Player->>Server: JOIN_PLAYER {gameId, playerName}
    Server-->>Administrator: PLAYER_JOINED {player}
    Server-->>All Players: PLAYER_JOINED {player}

    Administrator->>Server: START_GAME {gameId}
    Server-->>All: GAME_STARTED

    Administrator->>Server: CHANGE_PHASE {gameId, newPhase}
    Server-->>All: PHASE_CHANGED {newPhase}

    Administrator->>Server: CHANGE_QUESTION {gameId, newQuestion}
    Server-->>All: QUESTION_CHANGED {newQuestion}

    Player->>Server: ADD_ANSWER {gameId, playerId, answer}
    Server-->>Administrator: ADD_ANSWER {player, answer}
