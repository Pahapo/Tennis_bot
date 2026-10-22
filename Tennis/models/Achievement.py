from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class Achievement(AsyncAttrs, Base):
    __tablename__ = "achievements"
    id_achievement = Column(Integer, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, nullable=False)
    achievement = Column(String(30), nullable=False)    # id из списка ACHIEVEMENTS в handlers/achievements.py
    date = Column(DateTime, nullable=False)
    seen = Column(Boolean, nullable=False)              # Игрок уже видел окно с поздравлением


    # Конструктор __init__
    def __init__(self, tg_user_id, achievement, date, seen=False):
        self.tg_user_id = tg_user_id
        self.achievement = achievement
        self.date = date
        self.seen = seen
