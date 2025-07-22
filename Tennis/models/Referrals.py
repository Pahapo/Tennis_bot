from sqlalchemy import Column, String, Integer, BigInteger
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class Referrals(AsyncAttrs, Base):
    __tablename__ = "referrals"
    tg_users_id = Column(BigInteger, primary_key=True, unique=True)
    referrals = Column(String(250), nullable=False)
    count = Column(Integer)


    # Конструктор __init__
    def __init__(self, tg_users_id, referrals=None, count=None):
        self.tg_users_id = tg_users_id
        self.referrals = referrals
        self.count = count