from constants import events
import models
from fastapi.encoders import jsonable_encoder

async def handle_player_join(data, db, manager, game_code: str):
    """Crea un jugador y notifica a todos los clientes."""
    print(f"Vamos a manejar el join de {data}")
    player_name = data.get("player")
    if not player_name:
        return

    game = db.query(models.Game).filter(models.Game.code == game_code).first()
    print(f"game: {game.code}")
    if not game:
        return

    print(f"Uniendo al jugador {player_name} a la partida {game.code}")

    # Crear jugador en la base de datos
    new_player = models.Player(name=player_name, game_id=game.id, is_admin=player_name=="administrator")
    db.add(new_player)
    db.commit()
    db.refresh(new_player)

    encoded_game = game.to_dict(include_players=True)
    print(f"encoded_game: {encoded_game}")

    await manager.broadcast(
        game_code,
        events.ServerEvents.PLAYER_JOINED, 
        {"game": encoded_game}
    )

async def handle_player_leave(data, db, manager, game_code: str):
    """Elimina un jugador y notifica a todos los clientes."""
    player_name = data.get("name")
    if not player_name:
        return

    game = db.query(models.Game).filter(models.Game.code == game_code).first()
    if not game:
        return

    player = (
        db.query(models.Player)
        .filter(models.Player.game_id == game.id, models.Player.name == player_name)
        .first()
    )

    if player:
        db.delete(player)
        db.commit()

    # Obtener lista actualizada
    players = [p.name for p in game.players]
    await manager.broadcast(
        game_code,
        {"type": "players_update", "players": players}
    )
