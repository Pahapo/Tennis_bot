from sqlalchemy import Column, Integer, BigInteger, Float, String, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class PaymentRequest(AsyncAttrs, Base):
    __tablename__ = "payment_requests"
    id_request = Column(Integer, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, nullable=False)
    tournament_id = Column(Integer, nullable=False)
    division_level = Column(Integer, nullable=False)        # В каком дивизионе играет (для второго дивизиона — другой)
    price = Column(Float, nullable=False)                   # Сколько игрок заплатил (с учётом скидки)
    crystals = Column(Integer, nullable=False)              # Сколько кристаллов списать после подтверждения
    photo = Column(String(100), nullable=False)             # Файл чека в Tennis/img/payment
    status = Column(String(20), nullable=False)             # pending — на проверке, ok — подтверждено, rejected — оплата не получена
    date = Column(DateTime, nullable=False)


    # Конструктор __init__
    def __init__(self, tg_user_id, tournament_id, division_level, price, crystals, photo, date, status='pending'):
        self.tg_user_id = tg_user_id
        self.tournament_id = tournament_id
        self.division_level = division_level
        self.price = price
        self.crystals = crystals
        self.photo = photo
        self.date = date
        self.status = status
