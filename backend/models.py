from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.inspection import inspect


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(8), unique=True, index=True)
    name = Column(String(100), nullable=False, default="Nueva partida")
    phase = Column(Integer, default=1)

    players = relationship("Player", back_populates="game", cascade="all, delete")
    game_questions = relationship("GameQuestion", back_populates="game", cascade="all, delete")

    def to_dict(self, include_players=False):
        data = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        if include_players:
            data["players"] = [p.to_dict() for p in self.players]
        return data


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"))
    is_admin = Column(Boolean, default=False)

    game = relationship("Game", back_populates="players")
    answers = relationship("Answer", back_populates="player", cascade="all, delete")

    def to_dict(self, include_game=False):
        data = {
            "id": self.id,
            "name": self.name,
            "game_id": self.game_id,
            "is_admin": self.is_admin,
        }
        if include_game and self.game:
            data["game"] = {
                "id": self.game.id,
                "code": self.game.code,
                "name": self.game.name,
                "phase": self.game.phase,
            }
        return data


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    phase = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)
    text = Column(String(255), nullable=False)
    type = Column(String(50), default="text")  # 'song', 'choice', etc.

    # Relación no obligatoria, solo para referencia inversa
    game_questions = relationship("GameQuestion", back_populates="base_question")


class GameQuestion(Base):
    __tablename__ = "game_questions"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    base_question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    text = Column(String(255), nullable=False)
    phase = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)

    game = relationship("Game", back_populates="game_questions")
    base_question = relationship("Question", back_populates="game_questions")
    answers = relationship("Answer", back_populates="game_question", cascade="all, delete")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    game_question_id = Column(Integer, ForeignKey("game_questions.id"), nullable=False)
    text = Column(Text, nullable=True)
    spotify_id = Column(String(50), nullable=True)
    correct = Column(Integer, default=0)

    player = relationship("Player", back_populates="answers")
    game_question = relationship("GameQuestion", back_populates="answers")

    def to_dict(self, include_game=False):
        data = {
            "id": self.id,
            "player_id": self.player_id,
            "game_question_id": self.game_question_id,
            "text": self.text,
            "spotify_id": self.spotify_id,
            "correct": self.correct,
        }
        return data


class Guess(Base):
    __tablename__ = "guesses"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)  # who guessed
    answer_id = Column(Integer, ForeignKey("answers.id"), nullable=False)  # which answer they guessed about
    guessed_player_id = Column(Integer, ForeignKey("players.id"), nullable=True)  # who they guessed

    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "answer_id": self.answer_id,
            "guessed_player_id": self.guessed_player_id,
        }
