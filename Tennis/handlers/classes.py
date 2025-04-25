from aiogram.fsm.state import State, StatesGroup

from config.db import session
from models.User import User
from models.Division import Division


class SendMessage(StatesGroup):
    message = State()

class RegPlayerStates(StatesGroup):
    id = State()
    name = State()
    link = State()
    age = State()
    sex = State()
    skills = State()
    time = State()

class PlayerData:     # НЕ ТРОГАТЬ !!!
    def __init__(self, id=None, name=None, link=None, age=None, sex=None, skills=None, time=None, ban=None, tournaments_list=None):
        self.id = id
        self.name = name
        self.link = link
        self.age = age
        self.sex = sex
        self.skills = skills
        self.time = time
        self.ban = ban
        self.tournaments_list = tournaments_list

    def __str__(self):             # НЕ ТРОГАТЬ !!!
        user = session.query(User).filter(User.tg_user_id == self.id).first()
        if user.division_level != None:
            name_division = session.query(Division).filter(Division.division_id == int(user.division_level)).first()
    
            if self.tournaments_list == None:            # исправить return под человеческий вид. Не должно быть 4 return. Предусмотреть проверку на self.tournaments_list == None и user.division_level != None
                return (
                    f"Имя: {self.name}\n"
                    f"Ссылка: <tg-spoiler>{self.link}</tg-spoiler>\n"
                    f"Возраст: {self.age}\n"
                    f"Пол: {self.sex}\n"
                    f"Дивизион: {name_division.name_division}\n" # Не определён
                    # f"Наличие бана: {self.ban}\n"
                    f"История турниров: Не участвовал(-а) 🥲\n"
                    f"Предпочтительное время игры: <blockquote>{self.time}</blockquote>\n"
                )
            else:
                return (
                    f"Имя: {self.name}\n"
                    f"Ссылка: <tg-spoiler>{self.link}</tg-spoiler>\n"
                    f"Возраст: {self.age}\n"
                    f"Пол: {self.sex}\n"
                    f"Дивизион: {name_division.name_division}\n"
                    # f"Наличие бана: {self.ban}\n"
                    f"История турниров: {self.tournaments_list}\n"
                    f"Предпочтительное время игры: <blockquote>{self.time}</blockquote>\n"
                )
        else:
            if self.tournaments_list == None:
                return (
                    f"Имя: {self.name}\n"
                    f"Ссылка: <tg-spoiler>{self.link}</tg-spoiler>\n"
                    f"Возраст: {self.age}\n"
                    f"Пол: {self.sex}\n"
                    f"Дивизион: Не определён\n"
                    # f"Наличие бана: {self.ban}\n"
                    f"История турниров: Не участвовал(-а) 🥲\n"
                    f"Предпочтительное время игры: <blockquote>{self.time}</blockquote>\n"
                )
            else:
                return (
                    f"Имя: {self.name}\n"
                    f"Ссылка: <tg-spoiler>{self.link}</tg-spoiler>\n"
                    f"Возраст: {self.age}\n"
                    f"Пол: {self.sex}\n"
                    f"Дивизион: Не определён\n"
                    # f"Наличие бана: {self.ban}\n"
                    f"История турниров: {self.tournaments_list}\n"
                    f"Предпочтительное время игры: <blockquote>{self.time}</blockquote>\n"
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
                "Имя": self.name,
                "Ссылка": self.link,
                "Возраст": self.age,
                "Пол": self.sex,
                "Дивизион": tournament_lvl,
                "Наличие бана": self.ban,
                "История турниров": self.tournaments_list,
                "Предпочтительное время игры": self.time
            }
        }


class RegTournamentPlayerStates(StatesGroup):
    id = State()
    name = State()
    link = State()
    level = State()
    time1 = State()
    time2 = State()
    selected_tournament = State()

class TournamentPlayerData:
    def __init__(self, id=None, name=None, link=None, level=None, time1=None, time2=None, selected_tournament=None):
        self.id = id
        self.name = name
        self.link = link
        self.level = level
        self.time1 = time1
        self.time2 = time2
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
            f"Время №1: {self.time1}\n"
            f"Время №2: {self.time2}\n"
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
                "Дивизион": tournament_lvl,
                "Время №1": self.time1,
                "Время №2": self.time2
            }
        }
    
    
class RegTournamentsStates(StatesGroup):
    name = State()
    address = State()
    level = State()
    count = State()
    time1 = State()
    time2 = State()
    price = State()
    regulations = State()


class TournamentsData:
    def __init__(self, name=None, address=None, level=None, count=None, time1=None, time2=None, price=None, regulations=None):
        self.name = name
        self.address = address
        self.level = level
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
            f"Адрес корта: {self.address}\n"
            f"Дивизион турнира: {tournament_lvl}\n"
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
                "Адрес корта": self.address,
                "Дивизион турнира": tournament_lvl,
                "Максимальное кол-во участников": self.count,
                "Начало": self.time1,
                "Окончание": self.time2,
                "Стоимость участия": self.price
            }
        }


class FindUser(StatesGroup):
    tg_user_id = State()
    name_ban = State()
    name_division = State()
    name_division_del_players = State()
    players_delete = State()
    link = State()
    level = State()
    period_ban = State()
    reason_ban = State()


# class RegInventoryStates(StatesGroup):
#     id = State()
#     name = State()
#     link = State()
#     description = State()
#     price = State()


# class InventoryData:     # НЕ ТРОГАТЬ !!!
#     def __init__(self, id=None, link=None, name=None, description=None, price=None):
#         self.id = id
#         self.link = link
#         self.name = name
#         self.description = description
#         self.price = price

    # def __str__(self):             # НЕ ТРОГАТЬ !!!
    #     list_inventory = session.query(Inventory).filter(Inventory.tg_user_id == self.id).all()
    #     if list_inventory != []:
    #         text_inventory = ''

    #         for inventory in list_inventory:
    #             text_inventory += f"Имя: {self.name}\nСсылка: <tg-spoiler>{self.link}</tg-spoiler>\nВозраст: {self.age}\nПол: {self.sex}\nДивизион: {name_division.name_division}\n"

    #         return text_inventory