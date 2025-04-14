from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router

from config.db import session
from models.Tournament import Tournament

router = Router()


def get_list_tournaments():
    tournaments_data = [row[0] for row in session.query(Tournament.name_tournament).all()]
    return tournaments_data


def create_tournaments_keyboard(tournament_names):
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=name)]
        for name in tournament_names
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)