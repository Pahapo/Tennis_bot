from aiogram.fsm.state import State, StatesGroup

from config.db import session
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
    payment_flag = State()
    message_flag = State()

class RegPlayerStates(StatesGroup):
    id = State()
    link = State()
    age = State()
    sex = State()
    booking = State()
    date_booking = State()
    date_without_booking = State()
    name_court = State()
    skills = State()
    comment = State()

class PlayerData:     # НЕ ТРОГАТЬ !!!
    def __init__(self, id=None, link=None, age=None, sex=None, date_booking=None, date_without_booking=None, name_court=None, skills=None, comment=None, ban=None, tournaments_list=None):
        self.id = id
        self.link = link
        self.age = age
        self.sex = sex
        self.date_booking = date_booking
        self.date_without_booking = date_without_booking
        self.name_court = name_court
        self.skills = skills
        self.comment = comment
        self.ban = ban
        self.tournaments_list = tournaments_list

    def __str__(self):             # НЕ ТРОГАТЬ !!!
        user = session.query(User).filter(User.tg_user_id == self.id).first()
        user_in_tournaments = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == self.id).all()
        tournament_ids = [games.id_tournament for games in user_in_tournaments]  # Получаем список ID игроков
        history_tournaments = session.query(Tournament).filter(Tournament.tournament_id.in_(tournament_ids)).all()

        text_card =  f"Имя: {user.name_user}\nСсылка: <tg-spoiler>{user.link}</tg-spoiler>\n"

        history = ''

        for toutnament in history_tournaments:
            if history == '':
                history += f"\"{toutnament.name_tournament}\""
            else:
                history += f", \"{toutnament.name_tournament}\""

        if history == '':
            history += 'не участвовал(-а) 🥲'

        text_card += f"История турниров: {history}\n"

        if self.sex:
            text_card += f"Пол: {self.sex}\n"
        else:
            text_card += f"Пол: {user.sex}\n"

        if self.age:
            text_card += f"Возраст: {self.age}\n"
        else:
            text_card += f"Возраст: {user.age}\n"
            
        if user.division_level != None:
            name_division = session.query(Division).filter(Division.division_id == int(user.division_level)).first()
            text_card += f"Дивизион: {name_division.name_division}\n"
        else:
            text_card += f"Дивизион: Не определён\n" # Добавить выбор дивизиона
            
        if self.date_booking:
            text_card += f"\nБронь корта: на {self.date_booking}\n"
            if self.name_court:
                text_card += f"Корт: {self.name_court}\n"
        else:
            text_card += f"\nБрони нет! Предлагаю поиграть: {self.date_without_booking}\n"

        if self.comment:
            text_card += f"Комментарий: <blockquote>{self.comment}</blockquote>\n"
        return text_card
            
    
    def get_data(self):
        user = session.query(User).filter(User.tg_user_id == self.id).first()
        levelTournament_list = list(map(int, self.level.split(",")))
        name_division = session.query(Division).all()
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
                "Предложение о дате игры": self.date_without_booking,
                "Комментарий": self.comment
            }
        }


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
        levelTournament_list = list(map(int, self.level.split(",")))
        name_division = session.query(Division).all()
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
    
    def get_data(self):
        levelTournament_list = list(map(int, self.level.split(",")))
        name_division = session.query(Division).all()
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
        if self.level != None:
            levelTournament_list = list(map(int, self.level.split(",")))
            name_division = session.query(Division).all()
            # Создаём словарь {division_id: name}, чтобы быстрее искать названия
            division_dict = {div.division_id: div.name_division for div in name_division}
            # Преобразуем список ID в список названий
            levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]
            tournament_lvl = ", ".join(levelTournament_names)


        return (
            f"Название турнира: {self.name}\n"
            f"Дивизион турнира: {tournament_lvl}\n"
            f"Тип турнира: {self.type}\n"
            f"Максимальное кол-во участников: {self.count} чел.\n"
            f"Начало: {self.time1}\n"
            f"Окончание: {self.time2}\n"
            f"Стоимость участия: {self.price} бел.руб.\n"
        )
    
    def get_data(self):
        levelTournament_list = list(map(int, self.level.split(",")))
        name_division = session.query(Division).all()
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
    name_kassa = State()
    name_division = State()
    name_division_del_players = State()
    players_delete = State()
    link = State()
    level = State()
    score = State()
    period_ban = State()
    reason_ban = State()


class UsedCoins(StatesGroup):
    coins = State()