from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from websocket.manager import websocket_endpoint
from sqlalchemy.orm import Session
import random, string
from database import get_db
from database import Base, engine, SessionLocal
import models, schemas

# Crear las tablas automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Furor API")

# --------------------
# CORS
# --------------------
origins = [
    "http://localhost:5173",  # Vue local
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # puedes usar ["*"] en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --------------------
# ENDPOINTS
# --------------------

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

app.add_api_websocket_route("/ws/{game_code}", websocket_endpoint)