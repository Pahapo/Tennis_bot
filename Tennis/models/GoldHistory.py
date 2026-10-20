from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class GoldHistory(AsyncAttrs, Base):
    __tablename__ = "gold_history"
    id_history = Column(Integer, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, nullable=False)
    amount = Column(Integer, nullable=False)                # +начисление / -трата
    reason = Column(String(30), nullable=False)             # daily, streak, referral, match_win, match_loss, skin
    comment = Column(String(100))
    date = Column(DateTime, nullable=False)


    # Конструктор __init__
    def __init__(self, tg_user_id, amount, reason, date, comment=None):
        self.tg_user_id = tg_user_id
        self.amount = amount
        self.reason = reason
        self.date = date
        self.comment = comment
