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
        if self.tournaments_list == None:
            return (
                f"Имя: {self.name}\n"
                f"Ссылка: <tg-spoiler>{self.link}</tg-spoiler>\n"
                f"Возраст: {self.age}\n"
                f"Пол: {self.sex}\n"
                f"Дивизион: {self.skills}\n"
                # f"Наличие бана: {self.ban}\n"
                f"История турниров: не участвовал 🥲\n"
                f"Предпочтительное время игры: <blockquote>{self.time}</blockquote>\n"
            )
        else:
            return (
                f"Имя: {self.name}\n"
                f"Ссылка: <tg-spoiler>{self.link}</tg-spoiler>\n"
                f"Возраст: {self.age}\n"
                f"Пол: {self.sex}\n"
                f"Дивизион: {self.skills}\n"
                # f"Наличие бана: {self.ban}\n"
                f"История турниров: {self.tournaments_list}\n"
                f"Предпочтительное время игры: <blockquote>{self.time}</blockquote>\n"
            )
    
    def get_data(self):
        return {
            self.id : 
            {
                "Имя": self.name,
                "Ссылка": self.link,
                "Возраст": self.age,
                "Пол": self.sex,
                "Дивизион": self.skills,
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
        return (
            f"Название турнира: <b>{self.name}</b>\n"
            f"Имя: {self.name}\n"
            f"Ссылка: <tg-spoiler>{self.link}</tg-spoiler>\n"
            f"Дивизион: {self.level}\n"
            f"Время №1: {self.time1}\n"
            f"Время №2: {self.time2}\n"
        )
    
    def get_data(self):
        return {
            self.id : 
            {
                "Название турнира": self.name,
                "Имя": self.name,
                "Ссылка": self.link,
                "Дивизион": self.level,
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

    def __str__(self):   # ИСПРАВИТЬ ! ! ! (в бд у нас список из цифр в текстовом виде)
        if self.level != None:
            division_lvl = ''
            array_level = self.level
            count_level = 0

            for level in list(map(int, array_level.split(","))): # делаем массив из цифр
                if count_level > 0:
                    division_lvl += ', '

                if int(self.level) == 1:
                    division_lvl += 'Золотой 🥇'
                elif int(self.level) == 2:
                    division_lvl += 'Серебряный 🥈'
                elif int(self.level) == 3:
                    division_lvl += 'Бронзовый 🥉'
                elif int(self.level) == 4:
                    division_lvl += 'Медный 🎾'
                elif int(self.level) == 5:
                    division_lvl += 'Железный 🏃‍♂️'
                else:
                    division_lvl = 'Все дивизионы'
                
                count_level += 1

        return (
            f"Название турнира: {self.name}\n"
            f"Адрес корта: {self.address}\n"
            f"Дивизион турнира: {division_lvl}\n"
            f"Максимальное кол-во участников: {self.count} чел.\n"
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
                "Дивизион турнира": self.level,
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