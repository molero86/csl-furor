from pydantic import BaseModel
from typing import List, Optional

class PlayerBase(BaseModel):
    name: str

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int
    class Config:
        orm_mode = True

class GameBase(BaseModel):
    name: Optional[str] = "Nueva partida"

class GameCreate(GameBase):
    pass

class Game(GameBase):
    id: int
    code: str
    phase: int
    players: List[Player] = []
    class Config:
        orm_mode = True
