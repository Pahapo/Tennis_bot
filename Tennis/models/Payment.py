from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from config.db import Base

class Payment(Base):
    __tablename__ = "payment"
    id_payment = Column(Integer, primary_key=True, autoincrement=True)
    id_tournament = Column(Integer, nullable=False)
    id_tg_user = Column(Integer, nullable=False)
    price = Column(String(10), nullable=False)
    coins = Column(String(10), nullable=False)
    photo = Column(String(100), nullable=False)
    salesman = Column(String(20), nullable=False)
    date = Column(DateTime, nullable=False)


    # Конструктор __init__
    def __init__(self, id_tournament, id_tg_user, price, date, coins=None, photo=None, salesman=None):
        # self.id_payment = id_payment
        self.id_tournament = id_tournament
        self.id_tg_user = id_tg_user
        self.price = price
        self.date = date
        self.coins = coins
        self.photo = photo
        self.salesman = salesman
