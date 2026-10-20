from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class PlayerSkin(AsyncAttrs, Base):
    __tablename__ = "player_skins"
    id_skin = Column(Integer, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, nullable=False)
    skin_id = Column(String(30), nullable=False)    # id из списка SKINS в handlers/skins.py
    date = Column(DateTime, nullable=False)


    # Конструктор __init__
    def __init__(self, tg_user_id, skin_id, date):
        self.tg_user_id = tg_user_id
        self.skin_id = skin_id
        self.date = date
