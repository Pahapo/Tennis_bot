from sqlalchemy import Column, Integer, String, Boolean, BigInteger
from config.db import Base

from config.db import session
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

        return f"Имя: {self.name_user}\nВозраст: {self.age}\nПол: {self.sex}\nДивизион: {self.division_level}\nИстория турниров: {history}\nНаличие бана: {self.ban_status} (До {self.end_date_ban})\n" 