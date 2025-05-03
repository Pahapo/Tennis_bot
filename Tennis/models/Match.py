from sqlalchemy import Column, Integer, String
from config.db import Base

class Match(Base):
    __tablename__ = "match"
    match_id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    id_tg_user = Column(Integer, nullable=False)
    date_booking = Column(String(40), nullable=False)
    date_without_booking = Column(String(40), nullable=False)
    comment = Column(String(300), nullable=False)
    player_1 = Column(Integer, nullable=False)
    player_2 = Column(Integer, nullable=False)


    # Конструктор __init__
    def __init__(self, id_tg_user, date_booking=None, date_without_booking=None, comment=None, player_1=None, player_2=None):
        self.id_tg_user = id_tg_user
        self.date_booking = date_booking
        self.date_without_booking = date_without_booking
        self.comment = comment
        self.player_1 = player_1
        self.player_2 = player_2