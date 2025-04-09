from sqlalchemy import Column, Integer, String
from db import Base

class Contestant(Base):
    __tablename__ = "contestant"
    contestant_id = Column(Integer, primary_key=True, unique=True)
    id_tg_user = Column(Integer, nullable=False)
    free_time_for_play = Column(String(100), nullable=False)


    # Конструктор __init__
    def __init__(self, contestant_id, id_tg_user, free_time_for_play):
        self.contestant_id = contestant_id
        self.id_tg_user = id_tg_user
        self.free_time_for_play = free_time_for_play