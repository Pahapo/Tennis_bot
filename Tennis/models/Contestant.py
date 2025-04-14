from sqlalchemy import Column, Integer, String
from config.db import Base

class Contestant(Base):
    __tablename__ = "contestant"
    contestant_id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    id_tg_user = Column(Integer, nullable=False)
    free_time_for_play = Column(String(200), nullable=False)


    # Конструктор __init__
    def __init__(self, id_tg_user, free_time_for_play):
        self.id_tg_user = id_tg_user
        self.free_time_for_play = free_time_for_play