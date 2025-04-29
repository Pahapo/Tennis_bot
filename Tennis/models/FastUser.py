from sqlalchemy import Column, Integer, BigInteger
from config.db import Base

class FastUser(Base):
    __tablename__ = "fast_booking_players"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id_user = Column(BigInteger, unique=True)


    # Конструктор __init__
    def __init__(self, tg_id_user):
        # self.user_id = user_id
        self.tg_id_user = tg_id_user
