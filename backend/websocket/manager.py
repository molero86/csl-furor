from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
import models
from database import get_db
from .handlers import handle_player_join, handle_player_leave
import constants.events as events

class ConnectionManager:
    def __init__(self):
        # Estructura: { "ABC123": [websocket1, websocket2, ...] }
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, game_code: str, websocket: WebSocket):
        await websocket.accept()
        if game_code not in self.active_connections:
            self.active_connections[game_code] = []
        self.active_connections[game_code].append(websocket)

    def disconnect(self, game_code: str, websocket: WebSocket):
        if game_code in self.active_connections:
            self.active_connections[game_code].remove(websocket)
            if not self.active_connections[game_code]:
                del self.active_connections[game_code]

    async def broadcast(self, game_code: str, type: str, message: dict):
        """Enviar un mensaje a todos los clientes conectados a una partida"""
        print(f"Broadcast a {game_code} -> {len(self.active_connections.get(game_code, []))} conexiones activas")
        if game_code in self.active_connections:
            for idx, connection in enumerate(self.active_connections[game_code]):
                print(f"  Enviando a conexión #{idx}: {connection.client}")
                # await connection.send_json({"type": type, **message})
                #sending example message to broadcast
                await connection.send_json({"type": type, "data": {**message}})
                


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, game_code: str, db: Session = Depends(get_db)):
    print("Nueva llamada a websocket_endpoint")
    """Punto de entrada del WebSocket para cada partida."""
    await manager.connect(game_code, websocket)

    try:
        # Comprobar que la partida existe
        game = db.query(models.Game).filter(models.Game.code == game_code).first()
        if not game:
            await websocket.send_json({"error": "Game not found"})
            await websocket.close()
            return

        while True:
            data = await websocket.receive_json()
            print(f"Data recibido de websocket_endpoint {data}")
            action = data.get("action")
            print(f"Action: {action}")

            if action == events.ClientEvents.JOIN_GAME:
                await handle_player_join(data, db, manager, game_code)
            elif action == events.ClientEvents.LEAVE_GAME:
                await handle_player_leave(data, db, manager, game_code)
            else:
                await websocket.send_json({"error": f"Unknown action: {action}"})

    except WebSocketDisconnect:
        manager.disconnect(game_code, websocket)
        print(f"Cliente desconectado de la partida {game_code}")
