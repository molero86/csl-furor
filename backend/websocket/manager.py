from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, List
import models
from database import SessionLocal
from .handlers import (
    handle_player_join,
    handle_player_leave,
    handle_player_answer,
    handle_game_phase_update,
    handle_change_question,
)
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

async def websocket_endpoint(websocket: WebSocket, game_code: str):
    print(f"🔌 Nueva conexión WebSocket solicitada para partida: {game_code}")
    """Punto de entrada del WebSocket para cada partida."""
    
    try:
        # Comprobar que la partida existe ANTES de aceptar (usar sesión corta)
        db0 = SessionLocal()
        try:
            game = db0.query(models.Game).filter(models.Game.code == game_code).first()
            if not game:
                print(f"❌ Partida {game_code} NO ENCONTRADA en BD")
                await websocket.accept()
                await websocket.send_json({"error": "Game not found"})
                await websocket.close()
                return
            else:
                print(f"✅ Partida {game_code} encontrada (ID: {game.id})")
        finally:
            db0.close()
        
        # Solo conectar si la partida existe
        await manager.connect(game_code, websocket)

        while True:
            data = await websocket.receive_json()
            print(f"Data recibido de websocket_endpoint {data}")
            action = data.get("action")
            print(f"Action: {action}")

            # Crear una sesión corta por cada mensaje para evitar transacciones largas
            db = SessionLocal()
            try:
                if action == events.ClientEvents.JOIN_GAME:
                    await handle_player_join(data, db, manager, game_code)
                elif action == events.ClientEvents.LEAVE_GAME:
                    await handle_player_leave(data, db, manager, game_code)
                elif action == events.ClientEvents.SEND_ANSWER:
                    await handle_player_answer(data, db, manager)
                elif action == events.ClientEvents.CHANGE_QUESTION:
                    # Admin requested question change
                    await handle_change_question(data, db, manager, game_code)
                elif action == events.ClientEvents.CHANGE_PHASE:
                    # Admin requested phase change - reuse existing handler
                    await handle_game_phase_update(data, db, manager, game_code)
                else:
                    await websocket.send_json({"error": f"Unknown action: {action}"})
            finally:
                db.close()

    except WebSocketDisconnect:
        manager.disconnect(game_code, websocket)
        print(f"Cliente desconectado de la partida {game_code}")
