from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from websocket.manager import manager
from websocket.handlers import handle_game_phase_update
from websocket.manager import websocket_endpoint
from sqlalchemy.orm import Session
import random, string, os
from dotenv import load_dotenv
from database import get_db

load_dotenv()
from database import Base, engine, SessionLocal
import models, schemas
from models import Game, Question, GameQuestion

# Crear las tablas automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Furor API")

# --------------------
# CORS - configurable via CORS_ORIGINS env var
# --------------------
cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:4018,http://localhost:4018,http://192.168.68.10:4018"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --------------------
# ENDPOINTS
# --------------------

# GAMES ---------------------------------------------------------------------------------------------------------------------------------
@app.post("/games", response_model=schemas.Game)
def create_game(db: Session = Depends(get_db)):
    code = generate_code()
    db_game = models.Game(name=code, code=code)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

@app.get("/games", response_model=list[schemas.Game])
def get_games(db: Session = Depends(get_db)):
    return db.query(models.Game).all()

@app.get("/games/{game_code}")
def get_game(game_code: str, db: Session = Depends(get_db)):
    game = db.query(models.Game).filter(models.Game.code == game_code).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@app.post("/games/{game_id}/generate-phase/{phase}")
async def generate_phase(game_id: str, phase: int, db: Session = Depends(get_db)):
    # 1️⃣ Verificar que la partida existe
    print("Generating phase", phase, "for game", game_id)
    game = db.query(Game).filter(Game.code == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # 2️⃣ Comprobar si la fase ya fue generada
    existing = db.query(GameQuestion).filter(
        GameQuestion.game_id == game.id,
        GameQuestion.phase == phase
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail=f"Phase {phase} already generated for this game")

    # 3️⃣ Obtener preguntas comunes de esa fase
    base_questions = db.query(Question).filter(Question.phase == phase).order_by(Question.order).all()
    if not base_questions:
        raise HTTPException(status_code=404, detail=f"No common questions found for phase {phase}")

    # 4️⃣ Crear las preguntas de la partida (copiar)
    game_questions = []
    for q in base_questions:
        gq = GameQuestion(
            game_id=game.id,
            base_question_id=q.id,
            text=q.text,
            phase=q.phase,
            order=q.order
        )
        db.add(gq)
        game_questions.append(gq)

    db.commit()

    await handle_game_phase_update({"phase": phase}, db, manager, game.code)

    # 5️⃣ Devolver resultado
    return {
        "success": True,
        "game_id": game_id,
        "phase": phase,
        "count": len(game_questions)
    }

@app.get("/games/{game_id}/phases/{phase}/questions")
def get_phase_questions(game_id: str, phase: int, db: Session = Depends(get_db)):
    # 1️⃣ Verificar que la partida existe
    game = db.query(Game).filter(Game.code == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # 2️⃣ Buscar las preguntas de esa fase para esa partida
    questions = (
        db.query(GameQuestion)
        .filter(GameQuestion.game_id == game.id, GameQuestion.phase == phase)
        .order_by(GameQuestion.order)
        .all()
    )

    if not questions:
        raise HTTPException(status_code=404, detail=f"No questions found for phase {phase}")

    # 3️⃣ Devolver las preguntas
    return {
        "game_id": game_id,
        "phase": phase,
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "order": q.order,
                "base_question_id": q.base_question_id
            }
            for q in questions
        ]
    }

# PLAYERS ---------------------------------------------------------------------------------------------------------------------------------
@app.get("/games/{game_code}/players", response_model=list[schemas.Player])
def get_players(game_code: str, db: Session = Depends(get_db)):
    game = db.query(models.Game).filter(models.Game.code == game_code).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game.players

@app.post("/games/{game_code}/players", response_model=schemas.Player)
def add_player(game_code: str, player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    game = db.query(models.Game).filter(models.Game.code == game_code).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    db_player = models.Player(name=player.name, game_id=game.id)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@app.delete("/players/{player_id}")
def delete_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    db.delete(player)
    db.commit()
    return {"message": "Player deleted successfully"}

# QUESTIONS (CRUD) ---------------------------------------------------------------------------------------------------------------------------------
@app.get("/questions", response_model=list[schemas.Question])
def get_questions(db: Session = Depends(get_db)):
    return db.query(models.Question).order_by(models.Question.phase, models.Question.order).all()


@app.get("/questions/{question_id}", response_model=schemas.Question)
def get_question(question_id: int, db: Session = Depends(get_db)):
    q = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q


@app.post("/questions", response_model=schemas.Question)
def create_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    db_q = models.Question(**question.dict())
    db.add(db_q)
    db.commit()
    db.refresh(db_q)
    return db_q


@app.put("/questions/{question_id}", response_model=schemas.Question)
def update_question(question_id: int, question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    q = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    for key, value in question.dict().items():
        setattr(q, key, value)
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@app.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    q = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(q)
    db.commit()
    return {"message": "Question deleted successfully"}

app.add_api_websocket_route("/ws/{game_code}", websocket_endpoint)


# Answers for a given game_question (used in phase 2)
@app.get("/game_questions/{gq_id}/answers")
def get_answers_for_game_question(gq_id: int, db: Session = Depends(get_db)):
    answers = db.query(models.Answer).filter(models.Answer.game_question_id == gq_id).all()
    result = []
    for a in answers:
        player = db.query(models.Player).filter(models.Player.id == a.player_id).first()
        result.append({
            "id": a.id,
            "text": a.text,
            "spotify_id": a.spotify_id,
            "player_id": a.player_id,
            "player_name": player.name if player else None,
        })
    return {"question_id": gq_id, "answers": result}


@app.get("/games/{game_code}/phases/{phase}/game_questions")
def get_game_questions_for_phase(game_code: str, phase: int, db: Session = Depends(get_db)):
    game = db.query(models.Game).filter(models.Game.code == game_code).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    gqs = db.query(models.GameQuestion).filter(models.GameQuestion.game_id == game.id, models.GameQuestion.phase == phase).order_by(models.GameQuestion.order).all()
    result = []
    for gq in gqs:
        answer_count = db.query(models.Answer).filter(models.Answer.game_question_id == gq.id).count()
        result.append({
            "id": gq.id,
            "text": gq.text,
            "order": gq.order,
            "answer_count": answer_count,
        })
    return {"game_id": game_code, "phase": phase, "game_questions": result}