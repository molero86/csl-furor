from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(8), unique=True, index=True)  # ID visible para los jugadores
    name = Column(String(100), nullable=False, default="Nueva partida")
    phase = Column(Integer, default=1)

    players = relationship("Player", back_populates="game", cascade="all, delete")

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"))

    game = relationship("Game", back_populates="players")
