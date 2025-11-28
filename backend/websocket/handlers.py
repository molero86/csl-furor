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

async def handle_game_phase_update(data, db, manager, game_code: str):
    """Update the game phase and notify all clients."""
    print("Handling game phase update:", data)
    new_phase = data.get("phase")
    print("New phase:", new_phase)
    if new_phase is None:
        print("No new phase provided")
        return

    game = db.query(models.Game).filter(models.Game.code == game_code).first()
    if not game:
        print("Game not found")
        return

    print(f"Actualizando la fase del juego {game.code} a {new_phase}")

    game.phase = new_phase
    db.commit()
    print("Game phase updated in DB")

    await manager.broadcast(
        game_code,
        events.ServerEvents.PHASE_CHANGED,
        {"phase": new_phase}
    )


async def handle_change_question(data, db, manager, game_code: str):
    """Handle admin request to change the current question index and notify clients."""
    print("Handling change question:", data)
    question_index = data.get("question_index")
    if question_index is None:
        print("No question_index provided")
        return

    # Broadcast the question change to all clients of the game
    await manager.broadcast(
        game_code,
        events.ServerEvents.QUESTION_CHANGED,
        {"question_index": question_index}
    )

async def handle_player_answer(data, db, manager):
    """Handle the player answer and notify all clients."""
    print("Handling player answer:", data)
    answer = data.get("answer")
    print("Answer:", answer)
    game = db.query(models.Game).filter(models.Game.code == answer.get("game_code")).first()
    if not game:
        print("Game not found")
        return
    print("Searching player from game", answer.get("player_name"))
    player = db.query(models.Player).filter(models.Player.game_id == game.id, models.Player.name == answer.get("player_name")).first()
    if not player:
        print("Player not found")
        return
    new_answer = models.Answer(player_id=player.id, game_question_id=answer.get("question_id"), text=answer.get("text"), spotify_id=answer.get("spotify_id"))
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)
    await manager.broadcast(
        answer.get("game_code"),
        events.ServerEvents.NEW_ANSWER,
        {"answer": new_answer.to_dict()}
    )