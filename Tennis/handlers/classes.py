from aiogram.fsm.state import State, StatesGroup

from config.db_utils import get_db_readonly, get_db
from sqlalchemy import select
from models.User import User
from models.Division import Division
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers

class SendSkill(StatesGroup):
    name = State()
    skill = State()

class SendMessage(StatesGroup):
    message = State()
    invent = State()
    callback = State()
    link = State()
    payment_flag = State()
    message_flag = State()
    send_division = State()

class RegPlayerStates(StatesGroup):
    id = State()
    link = State()
    age = State()
    sex = State()
    booking = State()
    date_booking = State()
    date_without_booking = State()
    name_court = State()
    type_match = State()
    skills = State()
    comment = State()

class PlayerData:     # НЕ ТРОГАТЬ !!!
    def __init__(self, id=None, link=None, age=None, sex=None, date_booking=None, date_without_booking=None, name_court=None, type_match=None, skills=None, comment=None, ban=None, tournaments_list=None):
        self.id = id
        self.link = link
        self.age = age
        self.sex = sex
        self.date_booking = date_booking
        self.date_without_booking = date_without_booking
        self.name_court = name_court
        self.type_match = type_match
        self.skills = skills
        self.comment = comment
        self.ban = ban
        self.tournaments_list = tournaments_list

    def __str__(self):
        return "Для получения карточки игрока вызовите метод .build_text_card()"
    
    async def build_text_card(self):  # НЕ ТРОГАТЬ !!!
        async with get_db_readonly() as session:  # Используем контекстный менеджер

            user = (await session.scalars(select(User).where(User.tg_user_id == self.id))).first()
            user_in_tournaments = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == self.id))).all()
            tournament_ids = [games.id_tournament for games in user_in_tournaments]  # Получаем список ID игроков
            history_tournaments = (await session.scalars(select(Tournament).where(Tournament.tournament_id.in_(tournament_ids)))).all()

            text_card =  f"<b>Имя:</b> {user.name_user}\n<b>Ссылка:</b> <tg-spoiler>{user.link}</tg-spoiler>\n"

            history = ''

            for tournament in history_tournaments:
                if history == '':
                    history += f"\"{tournament.name_tournament}\""
                else:
                    history += f", \"{tournament.name_tournament}\""

            if history == '':
                history += 'не участвовал(-а) 🥲'

            text_card += f"<b>История турниров:</b> {history}\n"

            if self.sex:
                text_card += f"<b>Пол:</b> {self.sex}\n"
            else:
                text_card += f"<b>Пол:</b> {user.sex}\n"

            if self.age:
                text_card += f"<b>Возраст:</b> {self.age}\n"
            else:
                text_card += f"<b>Возраст:</b> {user.age}\n"
                
            if user.division_level != None:
                name_division = (await session.scalars(select(Division).where(Division.division_id == int(user.division_level)))).first()
                text_card += f"<b>Дивизион:</b> {name_division.name_division}\n"
            else:
                text_card += f"<b>Дивизион:</b> Не определён\n" # Добавить выбор дивизиона
                
            if self.date_booking:
                text_card += f"\n✅ <b>Бронь корта:</b> на {self.date_booking}\n<b>Корт:</b> {self.name_court}\n"
            else:
                text_card += f"\n❌ <b>Брони нет! Предлагаю поиграть:</b> {self.date_without_booking}\n"

            if self.type_match:
                text_card += f"<b>Тип игры:</b> {self.type_match}\n"

            if self.comment:
                text_card += f"<b>Комментарий:</b> <blockquote>{self.comment}</blockquote>\n"
            
            return text_card
            
    
    async def get_data(self):
        async with get_db_readonly() as session:  # Используем контекстный менеджер

            user = (await session.scalars(select(User).where(User.tg_user_id == self.id))).first()
            levelTournament_list = list(map(int, self.level.split(",")))
            name_division = (await session.scalars(select(Division))).all()
            # Создаём словарь {division_id: name}, чтобы быстрее искать названия
            division_dict = {div.division_id: div.name_division for div in name_division}
            # Преобразуем список ID в список названий
            levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]
            tournament_lvl = ", ".join(levelTournament_names)
        
            return {
                self.id : 
                {
                    "Ссылка": self.link,
                    "История турниров": self.tournaments_list,
                    "Пол": self.sex,
                    "Возраст": self.age,
                    "Дивизион": tournament_lvl,
                    "Бронь корта": self.date_booking,
                    "Корт": self.name_court,
                    "Тип игры": self.type_match,
                    "Предложение о дате игры": self.date_without_booking,
                    "Комментарий": self.comment
                }
            }


class PlayerDataAbout:     # НЕ ТРОГАТЬ !!!
    def __init__(self, id=None):
        self.id = id

    def __str__(self):
        return "Для получения информации о игроке вызовите метод .about_player()"
    
    async def about_player(self):  # НЕ ТРОГАТЬ !!!
        async with get_db_readonly() as session:  # Используем контекстный менеджер

            user = (await session.scalars(select(User).where(User.tg_user_id == self.id))).first()
            user_in_tournaments = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == self.id))).all()
            tournament_ids = [games.id_tournament for games in user_in_tournaments]  # Получаем список ID игроков
            history_tournaments = (await session.scalars(select(Tournament).where(Tournament.tournament_id.in_(tournament_ids)))).all()

            text_card =  f"<b>Имя:</b> {user.name_user}\n"

            if user.sex:
                text_card += f"<b>Пол:</b> {user.sex}\n"

            if user.age:
                text_card += f"<b>Возраст:</b> {user.age} лет\n"

            if user.division_level != None:
                name_division = (await session.scalars(select(Division).where(Division.division_id == int(user.division_level)))).first()
                text_card += f"\n<b>Дивизион:</b> {name_division.name_division}\n"
            else:
                text_card += f"\n<b>Дивизион:</b> Не определён\n"

            if user.rating != None and user.division_level != None:
                text_card += f"<b>Рейтинг:</b> {user.rating} ⚡️\n"

            history = ''

            for tournament in history_tournaments:
                if history == '':
                    history += f"\"{tournament.name_tournament}\""
                else:
                    history += f", \"{tournament.name_tournament}\""

            if history == '':
                history += "не участвовал(-а) 🥲"

            text_card += f"\n<b>История турниров:</b> {history}\n"
            
            if user_in_tournaments:
                text_card += f"<b>Количество сыгранных игр в турнирах:</b> {len(user_in_tournaments)} 🎾"

            return text_card



class RegTournamentPlayerStates(StatesGroup):
    id = State()
    name = State()
    link = State()
    level = State()
    selected_tournament = State()

class TournamentPlayerData:
    def __init__(self, id=None, name=None, link=None, level=None, selected_tournament=None):
        self.id = id
        self.name = name
        self.link = link
        self.level = level
        self.selected_tournament = selected_tournament

    def __str__(self):
        return "Для получения карточки игрока вызовите метод .build_text_card()"
    
    async def build_text_card(self):
        async with get_db_readonly() as session:  # Используем контекстный менеджер

            levelTournament_list = list(map(int, self.level.split(",")))
            name_division = (await session.scalars(select(Division))).all()

            # Создаём словарь {division_id: name}, чтобы быстрее искать названия
            division_dict = {div.division_id: div.name_division for div in name_division}
            # Преобразуем список ID в список названий
            levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]
            tournament_lvl = ", ".join(levelTournament_names)
        
            return (
                f"Название турнира: <b>{self.name}</b>\n"
                f"Имя: {self.name}\n"
                f"Ссылка: <tg-spoiler>{self.link}</tg-spoiler>\n"
                f"Дивизион: {tournament_lvl}\n"
            )
    
    async def get_data(self):
        async with get_db_readonly() as session:  # Используем контекстный менеджер
            levelTournament_list = list(map(int, self.level.split(",")))
            name_division = (await session.scalars(select(Division))).all()

            # Создаём словарь {division_id: name}, чтобы быстрее искать названия
            division_dict = {div.division_id: div.name_division for div in name_division}
            # Преобразуем список ID в список названий
            levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]
            tournament_lvl = ", ".join(levelTournament_names)

            return {
                self.id : 
                {
                    "Название турнира": self.name,
                    "Имя": self.name,
                    "Ссылка": self.link,
                    "Дивизион": tournament_lvl
                }
            }
        
    
class RegTournamentsStates(StatesGroup):
    name = State()
    level = State()
    type = State()
    img_flag = State()
    count = State()
    time1 = State()
    time2 = State()
    price = State()
    regulations = State()


class TournamentsData:
    def __init__(self, name=None, level=None, type=None, count=None, time1=None, time2=None, price=None, regulations=None):
        self.name = name
        self.level = level
        self.type = type
        self.count = count
        self.time1 = time1
        self.time2 = time2
        self.price = price
        self.regulations = regulations

    def __str__(self):
        return "Для получения карточки игрока вызовите метод .get_data_async()"

    async def get_data_async(self):
        if self.level != None:
            async with get_db_readonly() as session:  # Используем контекстный менеджер

                levelTournament_list = list(map(int, self.level.split(",")))
                name_division = (await session.scalars(select(Division))).all()
                
                # Создаём словарь {division_id: name}, чтобы быстрее искать названия
                division_dict = {div.division_id: div.name_division for div in name_division}
                # Преобразуем список ID в список названий
                levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]
                tournament_lvl = ", ".join(levelTournament_names)


        return (
            f"<b>Название турнира:</b> {self.name}\n"
            f"<b>Дивизион турнира:</b> {tournament_lvl}\n"
            f"<b>Тип турнира:</b> {self.type}\n"
            f"<b>Максимальное кол-во участников:</b> {self.count} чел.\n\n"
            f"<b>Дата:</b> {self.time1} - {self.time2}\n"
            f"<b>Стоимость участия:</b> {self.price} бел.руб.\n"
        )
    
    async def get_data(self):
        levelTournament_list = list(map(int, self.level.split(",")))

        async with get_db_readonly() as session:  # Используем контекстный менеджер
            name_division = (await session.scalars(select(Division))).all()

        # Создаём словарь {division_id: name}, чтобы быстрее искать названия
        division_dict = {div.division_id: div.name_division for div in name_division}
        # Преобразуем список ID в список названий
        levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]
        tournament_lvl = ", ".join(levelTournament_names)

        return {
            self.name : 
            {
                "Название турнира": self.name,
                "Дивизион турнира": tournament_lvl,
                "Тип турнира": self.type,
                "Максимальное кол-во участников": self.count,
                "Начало": self.time1,
                "Окончание": self.time2,
                "Стоимость участия": self.price
            }
        }


class FindUser(StatesGroup):
    tg_user_id = State()
    name_score = State()
    name_ban = State()
    name_rename = State()
    name_kassa = State()
    name_division = State()
    name_division_del_players = State()
    players_delete = State()
    link = State()
    level = State()
    score = State()
    rename = State()
    period_ban = State()
    reason_ban = State()


class UsedCoins(StatesGroup):
    coins = State()