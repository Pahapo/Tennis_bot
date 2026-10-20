from sqlalchemy import Column, BigInteger, Boolean, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class PendingReferral(AsyncAttrs, Base):
    __tablename__ = "pending_referrals"
    friend_id = Column(BigInteger, primary_key=True, unique=True)   # Кого пригласили
    referrer_id = Column(BigInteger, nullable=False)                # Кто пригласил
    rewarded = Column(Boolean, nullable=False)                      # Награда уже выдана (после первой игры друга)
    date = Column(DateTime, nullable=False)


    # Конструктор __init__
    def __init__(self, friend_id, referrer_id, date, rewarded=False):
        self.friend_id = friend_id
        self.referrer_id = referrer_id
        self.date = date
        self.rewarded = rewarded
