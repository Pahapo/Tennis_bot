from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router
from sqlalchemy import func

from config.db import session
from models.Tournament import Tournament


router = Router()

# Вывод кнопок под турнир

def get_list_tournaments():
    tournaments_data = [
        row.name_tournament for row in session.query(Tournament).filter(
            func.str_to_date(Tournament.start_tournament, "%d.%m.%Y") >= datetime.today()
        ).all()
    ]
    return tournaments_data


def create_tournaments_keyboard(tournament_names):
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"tournament_{name}")]
        for name in tournament_names
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='main_edit_tournament')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок под турнир для редактора

def get_list_tournaments_editor():
    tournaments_data = [
        row.name_tournament for row in session.query(Tournament).filter(
            func.str_to_date(Tournament.start_tournament, "%d.%m.%Y") >= datetime.today()
        ).all()
    ]
    return tournaments_data


def create_tournaments_keyboard_editor(tournament_names):
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=name)]
        for name in tournament_names
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='edit_tournament')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок под ссылку турнира

def get_links_tournaments():
    end_date = datetime.today() - timedelta(days = 3)
    tournaments_data = {
        row.name_tournament: row.link_table for row in session.query(Tournament).filter(
            func.str_to_date(Tournament.end_tournament, "%d.%m.%Y") >= end_date
        ).all()
    }
    return tournaments_data

# Вывод кнопок под  ссылку турнира, которые попали в архив

def get_history_links_tournaments():
    end_date = datetime.today() - timedelta(days = 3)
    tournaments_data = {
        row.name_tournament: row.link_table for row in session.query(Tournament).filter(
            func.str_to_date(Tournament.end_tournament, "%d.%m.%Y") < end_date
        ).all()
    }
    return tournaments_data


def create_links_tournaments_keyboard(tournaments_data):
    buttons = [
        [InlineKeyboardButton(text=name, url=link)]
        for name, link in tournaments_data.items()
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='tournament_table')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок под турнир для удаления участника

def get_list_tournaments_players():
    tournaments_data = [
        row.name_tournament+'_players' for row in session.query(Tournament).filter(
            func.str_to_date(Tournament.end_tournament, "%d.%m.%Y") >= datetime.today()
        ).all()
    ]
    return tournaments_data


def create_tournaments_keyboard_players(tournaments_data):
    buttons = [
        [InlineKeyboardButton(text=name.replace("_players", ""), callback_data=name)]
        for name in tournaments_data
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок для редактирования турнир

def get_list_tournaments_edit():
    tournaments_data = [
        row.name_tournament+'_edit' for row in session.query(Tournament).filter(
            func.str_to_date(Tournament.end_tournament, "%d.%m.%Y") >= datetime.today()
        ).all()
    ]
    return tournaments_data


def create_tournaments_edit_keyboard(tournaments_data):
    buttons = [
        [InlineKeyboardButton(text=name.replace("_edit", ""), callback_data=name)]
        for name in tournaments_data
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок для удаления турнира

def get_list_tournaments_delete():
    tournaments_data = [
        row.name_tournament+'_delete' for row in session.query(Tournament).filter(
            func.str_to_date(Tournament.end_tournament, "%d.%m.%Y") >= datetime.today()
        ).all()
    ]
    return tournaments_data


def create_tournaments_delete_keyboard(tournaments_data):
    buttons = [
        [InlineKeyboardButton(text=name.replace("_delete", ""), callback_data=name)]
        for name in tournaments_data
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)