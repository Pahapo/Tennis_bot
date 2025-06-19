from sqlalchemy import Column, Integer, String
from config.db import Base

class Match(Base):
    __tablename__ = "match"
    match_id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    id_tg_user = Column(Integer, nullable=False)
    date_booking = Column(String(40), nullable=False)
    date_without_booking = Column(String(40), nullable=False)
    name_court = Column(String(50), nullable=False)
    comment = Column(String(300), nullable=False)
    type = Column(String(15), nullable=False)
    player_1 = Column(Integer, nullable=False)
    player_2 = Column(Integer, nullable=False)
    player_3 = Column(Integer, nullable=False)
    player_4 = Column(Integer, nullable=False)


    # Конструктор __init__
    def __init__(self, id_tg_user, date_booking=None, date_without_booking=None, name_court=None, comment=None, type=None, player_1=None, player_2=None, player_3=None, player_4=None):
        self.id_tg_user = id_tg_user
        self.date_booking = date_booking
        self.date_without_booking = date_without_booking
        self.name_court = name_court
        self.comment = comment
        self.type = type
        self.player_1 = player_1
        self.player_2 = player_2
        self.player_3 = player_3
        self.player_4 = player_4