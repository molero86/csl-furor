from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.inspection import inspect

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(8), unique=True, index=True)  # ID visible para los jugadores
    name = Column(String(100), nullable=False, default="Nueva partida")
    phase = Column(Integer, default=1)

    players = relationship("Player", back_populates="game", cascade="all, delete")

    def to_dict(self, include_players=False):
        data = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        if include_players:
            data["players"] = [p.to_dict() for p in self.players]  # asumiendo que Player tiene to_dict()
        return data

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"))
    is_admin = Column(Integer, default=0)

    game = relationship("Game", back_populates="players")

    def to_dict(self, include_game=False):
        """Convierte el objeto Player a un diccionario serializable."""
        data = {
            "id": self.id,
            "name": self.name,
            "game_id": self.game_id,
            "is_admin": self.is_admin,
        }

        if include_game and self.game:
            # Evitamos incluir los jugadores dentro del game, para no crear recursión
            data["game"] = {
                "id": self.game.id,
                "code": self.game.code,
                "name": self.game.name,
                "phase": self.game.phase,
            }

        return data
