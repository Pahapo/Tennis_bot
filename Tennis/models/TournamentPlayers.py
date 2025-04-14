from sqlalchemy import Column, Integer, Boolean
from config.db import Base

class TournamentPlayers(Base):
    __tablename__ = "tournament_players"
    id_tournament_players = Column(Integer, autoincrement=True, primary_key=True)
    id_tournament = Column(Integer, nullable=False)
    id_tg_user = Column(Integer, nullable=False)
    time_workdays = Column(Boolean, nullable=False)
    time_weekends = Column(Boolean, nullable=False)


    def __init__(self, id_tournament, id_tg_user, time_workdays, time_weekends):
        self.id_tournament = id_tournament
        self.id_tg_user = id_tg_user
        self.time_workdays = time_workdays
        self.time_weekends = time_weekends