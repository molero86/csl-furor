from pydantic import BaseModel
from typing import List, Optional


# ---- PLAYERS ----
class PlayerBase(BaseModel):
    name: str


class PlayerCreate(PlayerBase):
    pass


class Player(PlayerBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True


# ---- GAMES ----
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


# ---- QUESTIONS ----
class QuestionBase(BaseModel):
    text: str
    phase: int
    order: int
    type: Optional[str] = "text"


class QuestionCreate(QuestionBase):
    pass


class Question(QuestionBase):
    id: int

    class Config:
        orm_mode = True


# ---- GAME QUESTIONS ----
class GameQuestionBase(BaseModel):
    text: str
    phase: int
    order: int
    base_question_id: int


class GameQuestion(GameQuestionBase):
    id: int
    game_id: int

    class Config:
        orm_mode = True


# ---- ANSWERS ----
class AnswerBase(BaseModel):
    text: Optional[str] = None
    spotify_id: Optional[str] = None
    correct: int = 0


class AnswerCreate(AnswerBase):
    player_id: int
    game_question_id: int


class Answer(AnswerBase):
    id: int
    player_id: int
    game_question_id: int

    class Config:
        orm_mode = True
