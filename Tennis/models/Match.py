from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class Match(AsyncAttrs, Base):
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
    status = Column(String(20))             # None — игра впереди, wait_score — ждём счёт, confirming — счёт на подтверждении, done — завершена
    score = Column(String(50))              # Счёт со стороны команды 1, например "6:4 3:6 7:5"
    team_1 = Column(String(50))             # ID игроков команды 1 через запятую
    team_2 = Column(String(50))             # ID игроков команды 2 через запятую
    score_author = Column(Integer)          # Кто ввёл счёт
    score_turn = Column(Integer)            # Если счёт отклонили — только этот игрок может ввести новый
    confirmed_by = Column(String(100))      # Кто уже подтвердил счёт (ID через запятую)
    reject_count = Column(Integer)          # Сколько раз счёт отклоняли
    reminder_sent = Column(Boolean)         # Напоминание за 2 часа до игры отправлено


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
        self.reject_count = 0
        self.reminder_sent = False
