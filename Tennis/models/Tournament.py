from sqlalchemy import Column, Integer, String
from config.db import Base

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
    link_table = Column(String(120))


    # Конструктор __init__
    def __init__(self, name_tournament, address, division, quantity_person, start_tournament, end_tournament, price, link_table):
        # self.tournament_id = tournament_id
        self.name_tournament = name_tournament
        self.address = address
        self.division = division
        self.quantity_person = quantity_person
        self.start_tournament = start_tournament
        self.end_tournament = end_tournament
        self.price = price
        self.link_table = link_table


    def __repr__(self):
        return f"Название: {self.name_tournament}\nАдрес: {self.address}\nДивизион турнира: {self.division}\nМаксимальное кол-во участников:{self.quantity_person}\nНачало:{self.start_tournament}\nОкончание:{self.end_tournament}" 