from sqlalchemy import Column, Integer, String, Boolean, BigInteger
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

from config.db_utils import get_db_readonly, get_db
from sqlalchemy import select
from models.Division import Division
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers

class User(AsyncAttrs, Base):
    __tablename__ = "users"
    tg_user_id = Column(BigInteger, primary_key=True, unique=True)
    name_user = Column(String(64), nullable=True)
    link = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)
    division_level = Column(Integer)
    ban_status = Column(Boolean)
    end_date_ban = Column(String(10))
    coins = Column(Integer)
    skill = Column(Integer)


    # Конструктор __init__
    def __init__(self, tg_user_id, name_user, link, age=None, sex=None, division_level=None, ban_status=None, end_date_ban=None, coins=None, skill=None):
        self.tg_user_id = tg_user_id
        self.name_user = name_user
        self.link = link
        self.age = age
        self.sex = sex
        self.division_level = division_level
        self.ban_status = ban_status
        self.end_date_ban = end_date_ban
        self.coins = coins
        self.skill = skill


    def __repr__(self):
        return "Для получения карточки игрока вызовите метод .build_repr_data()"

    async def build_repr_data(self):
        async with get_db_readonly() as session:  # Используем контекстный менеджер

            user_in_tournaments = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == self.tg_user_id))).all()
            tournament_ids = [games.id_tournament for games in user_in_tournaments]  # Получаем список ID игроков
            history_tournaments = (await session.scalars(select(Tournament).where(Tournament.tournament_id.in_(tournament_ids)))).all()

            history = ''

            for tournament in history_tournaments:
                if history == '':
                    history += f"\"{tournament.name_tournament}\""
                else:
                    history += f", \"{tournament.name_tournament}\""

            if history == '':
                history = 'не участвовал(-а) 🥲'

            if self.division_level != None:
                division = (await session.scalars(select(Division).where(Division.division_id == self.division_level))).first()
                division_lvl = division.name_division
            else: 
                division_lvl = 'Не определён'

            user = (await session.scalars(select(User).where(User.tg_user_id == self.tg_user_id))).first()

            text = f"<b>Имя:</b> {self.name_user}\n<b>История турниров:</b> {history}"
            
            if self.sex:
                text += f'\n<b>Пол:</b> {self.sex}'

            if self.age:
                text += f'\n<b>Возраст:</b> {self.age}'
            
            text += f'\n<b>Дивизион:</b> {division_lvl}'
            
            if user.ban_status == True:
                text += f'\n<b>Наличие бана:</b> до {user.end_date_ban}'

        return text