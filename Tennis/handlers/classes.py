from aiogram.fsm.state import State, StatesGroup


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

class PlayerData:
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

    def __str__(self):
        return (
            f"Имя: {self.name}\n"
            f"Ссылка: <tg-spoiler>{self.link}</tg-spoiler>\n"
            f"Возраст: {self.age}\n"
            f"Пол: {self.sex}\n"
            f"Уровень игры: {self.skills}\n"
            f"Предпочтительное время игры: <blockquote>{self.time}</blockquote>\n"
            # f"Наличие бана: {self.ban}\n"
            f"История турниров: {self.tournaments_list}"
        )
    
    def get_data(self):
        return {
            self.id : 
            {
                "Имя": self.name,
                "Ссылка": self.link,
                "Возраст": self.age,
                "Пол": self.sex,
                "Уровень игры": self.skills,
                "Предпочтительное время игры": self.time,
                "Наличие бана": self.ban,
                "История турниров": self.tournaments_list
            }
        }


class RegTournamentPlayerStates(StatesGroup):
    id = State()
    name = State()
    link = State()
    level = State()
    time1 = State()
    time2 = State()

class TournamentPlayerData:
    def __init__(self, id=None, name=None, link=None, level=None, time1=None, time2=None, tournament=None):
        self.id = id
        self.name = name
        self.link = link
        self.level = level
        self.time1 = time1
        self.time2 = time2

    def __str__(self):
        return (
            f"Имя: {self.name}\n"
            f"Ссылка: <tg-spoiler>{self.link}</tg-spoiler>\n"
            f"Уровень игры: {self.level}\n"
            f"Время №1: {self.time1}\n"
            f"Время №2: {self.time2}\n"
        )
    
    def get_data(self):
        return {
            self.id : 
            {
                "Имя": self.name,
                "Ссылка": self.link,
                "Уровень игры": self.level,
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


class TournamentsData:
    def __init__(self, name=None, address=None, level=None, count=None, time1=None, time2=None, price=None):
        self.name = name
        self.address = address
        self.level = level
        self.count = count
        self.time1 = time1
        self.time2 = time2
        self.price = price

    def __str__(self):
        return (
            f"Название турнира: {self.name}\n"
            f"Адрес корта: {self.address}\n"
            f"Уровень турнира: {self.level}\n"
            f"Максимальное кол-во участников: {self.count}\n"
            f"Начало: {self.time1}\n"
            f"Окончание: {self.time2}\n"
            f"Стоимость участия: {self.price} бел.руб.\n"
        )
    
    def get_data(self):
        return {
            self.name : 
            {
                "Название турнира": self.name,
                "Адрес корта": self.address,
                "Уровень турнира": self.level,
                "Максимальное кол-во участников": self.count,
                "Начало": self.time1,
                "Окончание": self.time2,
                "Стоимость участия": self.price
                # После прохождения турнира добавлять в карточку игрока название турнира, как история
            }
        }


class FindUser(StatesGroup):
    name = State()