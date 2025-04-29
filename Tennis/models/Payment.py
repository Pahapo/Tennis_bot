from sqlalchemy import Column, Integer, String
from config.db import Base

class Payment(Base):
    __tablename__ = "payment"
    id_player = Column(Integer, primary_key=True, autoincrement=True)
    id_tournament = Column(Integer, nullable=False)
    id_tg_user = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    photo = Column(String(100), nullable=False)


    # Конструктор __init__
    def __init__(self, id_tournament, id_tg_user, price, photo):
        # self.id_player = id_player
        self.id_tournament = id_tournament
        self.id_tg_user = id_tg_user
        self.price = price
        self.photo = photo
