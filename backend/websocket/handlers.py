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

    # Ensure game-specific questions for this phase exist (copy base questions if needed)
    existing = db.query(models.GameQuestion).filter(
        models.GameQuestion.game_id == game.id,
        models.GameQuestion.phase == new_phase
    ).first()

    if not existing:
        # copy base questions of that phase into game_questions
        base_questions = db.query(models.Question).filter(models.Question.phase == new_phase).order_by(models.Question.order).all()
        if base_questions:
            for q in base_questions:
                gq = models.GameQuestion(
                    game_id=game.id,
                    base_question_id=q.id,
                    text=q.text,
                    phase=q.phase,
                    order=q.order
                )
                db.add(gq)
        else:
            print(f"No common questions found for phase {new_phase} to copy into game {game.code}")

    db.commit()
    print("Game phase updated in DB and game questions ensured")

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
    payload = {"question_index": question_index}
    # If admin provided a specific game_question id (phase 2), include it
    if data.get("game_question_id"):
        payload["game_question_id"] = data.get("game_question_id")
    if data.get("game_question_text"):
        payload["game_question_text"] = data.get("game_question_text")

    await manager.broadcast(
        game_code,
        events.ServerEvents.QUESTION_CHANGED,
        payload
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


async def handle_player_guess(data, db, manager, game_code: str):
    """Handle a player's guesses (phase 2). Expects payload with 'guesses': [{answer_id, guessed_player_id}], and 'player_name'."""
    print("Handling player guess:", data)
    guesses = data.get("guesses") or []
    player_name = data.get("player_name")
    if not player_name or not guesses:
        print("No player_name or guesses provided")
        return

    game = db.query(models.Game).filter(models.Game.code == game_code).first()
    if not game:
        print("Game not found")
        return

    guesser = db.query(models.Player).filter(models.Player.game_id == game.id, models.Player.name == player_name).first()
    if not guesser:
        print("Guesser not found")
        return

    inserted = []
    for g in guesses:
        answer_id = g.get("answer_id")
        guessed_player_id = g.get("guessed_player_id")
        if not answer_id:
            continue
        new_g = models.Guess(player_id=guesser.id, answer_id=answer_id, guessed_player_id=guessed_player_id)
        db.add(new_g)
        inserted.append(new_g)

    db.commit()

    # Build aggregated data for the affected question
    # find the question id from one of the answers
    qid = None
    if inserted:
        ans = db.query(models.Answer).filter(models.Answer.id == inserted[0].answer_id).first()
        if ans:
            qid = ans.game_question_id

    # collect all guesses for answers in this question
    guesses_rows = []
    if qid is not None:
        # get all answers for that question
        answers = db.query(models.Answer).filter(models.Answer.game_question_id == qid).all()
        answer_ids = [a.id for a in answers]
        guesses_rows = db.query(models.Guess).filter(models.Guess.answer_id.in_(answer_ids)).all()

    # Prepare payload: mapping answer_id -> list of guess dicts
    mapping = {}
    for gr in guesses_rows:
        mapping.setdefault(gr.answer_id, []).append(gr.to_dict())

    await manager.broadcast(
        game_code,
        events.ServerEvents.GUESS_UPDATED,
        {"question_id": qid, "guesses": mapping}
    )


# Variable global para trackear el primer buzzer presionado por partida
buzzer_winners = {}

async def handle_buzzer_pressed(data, db, manager, game_code: str):
    """Handle buzzer press from a player. Only the first press is registered."""
    print("Handling buzzer press:", data)
    player_name = data.get("player_name")
    if not player_name:
        print("No player_name provided")
        return

    game = db.query(models.Game).filter(models.Game.code == game_code).first()
    if not game:
        print("Game not found")
        return

    player = db.query(models.Player).filter(
        models.Player.game_id == game.id, 
        models.Player.name == player_name
    ).first()
    
    if not player:
        print("Player not found")
        return

    # Check if someone already pressed the buzzer for this game
    if game_code in buzzer_winners and buzzer_winners[game_code] is not None:
        print(f"Buzzer already pressed by {buzzer_winners[game_code]}")
        return

    # Register this player as the winner
    buzzer_winners[game_code] = {
        "player_id": player.id,
        "player_name": player.name
    }
    
    print(f"🔔 Buzzer winner: {player.name}")

    # Broadcast to all clients who won
    await manager.broadcast(
        game_code,
        events.ServerEvents.BUZZER_WINNER,
        {
            "player_id": player.id,
            "player_name": player.name
        }
    )


async def handle_buzzer_reset(data, db, manager, game_code: str):
    """Reset buzzer state for the next song."""
    print(f"Resetting buzzer for game {game_code}")
    
    # Clear the winner for this game
    if game_code in buzzer_winners:
        buzzer_winners[game_code] = None
    
    # Broadcast reset to all clients
    await manager.broadcast(
        game_code,
        events.ServerEvents.BUZZER_RESET,
        {}
    )


async def handle_show_final_scores(data, db, manager, game_code: str):
    """Notify all players to navigate to final scores."""
    print(f"Admin requesting show final scores for game {game_code}")
    
    # Broadcast to all clients to navigate to final scores
    await manager.broadcast(
        game_code,
        events.ServerEvents.SHOW_FINAL_SCORES,
        {}
    )