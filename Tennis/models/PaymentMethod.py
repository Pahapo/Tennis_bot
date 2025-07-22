from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class PaymentMethod(AsyncAttrs, Base):
    __tablename__ = "payment_method"
    payment_method_id = Column(Integer, primary_key=True, autoincrement=True)
    payment_method = Column(String(40), nullable=False)
    bank_name = Column(String(25), nullable=False)


    # Конструктор __init__
    def __init__(self, payment_method, bank_name):
        self.payment_method = payment_method
        self.bank_name = bank_name
