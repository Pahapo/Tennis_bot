from sqlalchemy import Column, Integer, String, Text
from config.db import Base

class Inventory(Base):
    __tablename__ = "inventory"
    inventory_id = Column(Integer, primary_key=True, autoincrement=True)
    photo = Column(String(30), nullable=False)
    description = Column(Text(1500))


    # Конструктор __init__
    def __init__(self, photo, description):
        # self.tournament_id = tournament_id
        self.photo = photo
        self.description = description
