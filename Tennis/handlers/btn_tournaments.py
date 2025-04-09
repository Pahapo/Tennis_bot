import json
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router

from db import session
from models.Tournament import Tournament

router = Router()


def get_list_tournaments():
    # tr = Tournament(name_tournament = "Пекин", address="Центральная Европа - Теслы 16", division="Золотой", quantity_person=16, start_tournament="14.04.2025", end_tournament="07.05.2025", price=30)
    # trr = Tournament(name_tournament = "Белград", address="Тропические острова - Лученка 24", division="Бронзовый", quantity_person=16, start_tournament="21.05.2025", end_tournament="14.06.2025", price=30)
    # session.add(tr)
    # session.add(trr)
    # session.commit()
    tournaments_data = [row[0] for row in session.query(Tournament.name_tournament).all()]
    return tournaments_data
    # try:
    #     with open("tournaments.json", "r", encoding="utf-8") as file:
    #         tournaments_data = json.load(file)
    #         return [list(tournament.keys())[0] for tournament in tournaments_data]
    # except (FileNotFoundError, json.JSONDecodeError):
    #     return []

def create_tournaments_keyboard(tournament_names):
    buttons = [
        [InlineKeyboardButton(text=f'Турнир - {name} 🎾', callback_data=name)]
        for name in tournament_names
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)