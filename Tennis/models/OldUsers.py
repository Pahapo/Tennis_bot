from sqlalchemy import Column, Integer, BigInteger
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class OldUsers(AsyncAttrs, Base):
    __tablename__ = "old_users"
    tg_old_users_id = Column(BigInteger, primary_key=True, unique=True)
    division_level = Column(Integer)


    # Конструктор __init__
    def __init__(self, tg_old_users_id, division_level=None):
        self.tg_old_users_id = tg_old_users_id
        self.division_level = division_level