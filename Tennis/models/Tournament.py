from sqlalchemy import Column, Integer, String
from config.db import Base

from config.db import session
from models.Division import Division

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
        if self.division != None:
            levelTournament_list = list(map(int, self.division.split(",")))
            name_division = session.query(Division).all()
            # Создаём словарь {division_id: name}, чтобы быстрее искать названия
            division_dict = {div.division_id: div.name_division for div in name_division}
            # Преобразуем список ID в список названий
            levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]
            tournament_lvl = ", ".join(levelTournament_names)
        else: 
            tournament_lvl = 'Не определён'

        return f"Название: {self.name_tournament}\nАдрес: {self.address}\nДивизион турнира: {tournament_lvl}\nМаксимальное кол-во участников:{self.quantity_person}\nНачало:{self.start_tournament}\nОкончание:{self.end_tournament}" 