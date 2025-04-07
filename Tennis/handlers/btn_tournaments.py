import json
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router

router = Router()


def get_list_tournaments():
    try:
        with open("tournaments.json", "r", encoding="utf-8") as file:
            tournaments_data = json.load(file)
            return [list(tournament.keys())[0] for tournament in tournaments_data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def create_tournaments_keyboard(tournament_names):
    buttons = [
        [InlineKeyboardButton(text=f'Турнир - {name} 🎾', callback_data=name)]
        for name in tournament_names
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)