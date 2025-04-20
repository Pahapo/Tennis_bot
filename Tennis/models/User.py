from sqlalchemy import Column, Integer, String, Boolean, BigInteger
from config.db import Base
import handlers.functions as f

from config.db import session
from models.Division import Division
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers

class User(Base):
    __tablename__ = "users"
    tg_user_id = Column(BigInteger, primary_key=True, unique=True)
    name_user = Column(String(20), nullable=True)
    link = Column(String(30), nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)
    division_level = Column(Integer)
    ban_status = Column(Boolean)
    end_date_ban = Column(String(10))


    # Конструктор __init__
    def __init__(self, tg_user_id, name_user, link, age=None, sex=None, division_level=None, ban_status=None, end_date_ban=None):
        self.tg_user_id = tg_user_id
        self.name_user = name_user
        self.link = link
        self.age = age
        self.sex = sex
        self.division_level = division_level
        self.ban_status = ban_status
        self.end_date_ban = end_date_ban


    def __repr__(self):
        user_in_tournaments = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == self.tg_user_id).all()
        tournament_ids = [games.id_tournament for games in user_in_tournaments]  # Получаем список ID игроков
        history_tournaments = session.query(Tournament).filter(Tournament.tournament_id.in_(tournament_ids)).all()

        history = ''

        for toutnament in history_tournaments:
            if history == '':
                history += f"\"{toutnament.name_tournament}\""
            else:
                history += f", \"{toutnament.name_tournament}\""

        if history == '':
            history = 'не участвовал 🥲'

        if self.division_level != None:
            levelTournament_list = list(map(int, self.division_level.split(",")))
            name_division = session.query(Division).all()
            # Создаём словарь {division_id: name}, чтобы быстрее искать названия
            division_dict = {div.division_id: div.name_division for div in name_division}
            # Преобразуем список ID в список названий
            levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]
            tournament_lvl = ", ".join(levelTournament_names)
        else: 
            tournament_lvl = 'Не определён'

        f.check_ban_user(self.tg_user_id)

        user = session.query(User).filter(User.tg_user_id == self.tg_user_id).first()

        if user.ban_status == True:
            return f"Имя: {self.name_user}\nВозраст: {self.age}\nПол: {self.sex}\nДивизион: {tournament_lvl}\nИстория турниров: {history}\nНаличие бана: До {user.end_date_ban}\n" 
        else:
            return f"Имя: {self.name_user}\nВозраст: {self.age}\nПол: {self.sex}\nДивизион: {tournament_lvl}\nИстория турниров: {history}\n" 