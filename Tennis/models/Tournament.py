from sqlalchemy import Column, Integer, String
from db import Base

class Tournament(Base):
    __tablename__ = "tournament"
    tournament_id = Column(Integer, primary_key=True, autoincrement=True)
    name_tournament = Column(String(50), nullable=False)
    address = Column(String(40), nullable=False)
    division = Column(String(15), nullable=False)
    quantity_person = Column(Integer, nullable=False)
    start_tournament = Column(String(10), nullable=False)
    end_tournament = Column(String(10))
    price = Column(Integer)


    # Конструктор __init__
    def __init__(self, name_tournament, address, division, quantity_person, start_tournament, end_tournament, price):
        # self.tournament_id = tournament_id
        self.name_tournament = name_tournament
        self.address = address
        self.division = division
        self.quantity_person = quantity_person
        self.start_tournament = start_tournament
        self.end_tournament = end_tournament
        self.price = price


    def __repr__(self):
        return f"Название: {self.name_tournament}\nАдрес: {self.address}\nУровень турнира: {self.division}\nМаксимальное кол-во участников:{self.quantity_person}\nНачало:{self.start_tournament}\nОкончание:{self.end_tournament}" 
        # "История турниров": self.end_date_ban,
        # "Предпочтительное время игры": self.end_date_ban