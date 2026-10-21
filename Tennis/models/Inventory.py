from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class Inventory(AsyncAttrs, Base):
    __tablename__ = "inventory"
    inventory_id = Column(Integer, primary_key=True, autoincrement=True)
    photo = Column(String(30), nullable=False)
    description = Column(Text(1500))
    price = Column(Float, nullable=True)  # бел.руб. Если пусто — цена ищется в описании


    # Конструктор __init__
    def __init__(self, photo, description):
        self.photo = photo
        self.description = description
