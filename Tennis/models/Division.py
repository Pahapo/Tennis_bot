from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class Division(AsyncAttrs, Base):
    __tablename__ = "division"
    division_id = Column(Integer, primary_key=True)
    name_division = Column(String(50), nullable=False)


    # Конструктор __init__
    def __init__(self, name_division):
        self.name_division = name_division