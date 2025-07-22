from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_utils import get_db_readonly, get_db
from models.Tournament import Tournament


router = Router()


# Вывод кнопок под турнир
async def get_list_tournaments(session: AsyncSession):
    result = await session.execute(
        select(Tournament.name_tournament).where(
            func.str_to_date(Tournament.start_tournament, "%d.%m.%Y") >= datetime.today()
        )
    )
    return [row[0] for row in result.all()]


def create_tournaments_keyboard(tournament_names):
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"tournament_out_bnt_{name}")]
        for name in tournament_names
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок под турнир для администратора и главного редактора
def create_tournaments_keyboard_admin(tournament_names):
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"tournament_out_bnt_{name}")]
        for name in tournament_names
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='main_edit_tournament')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок под турнир для редактора
def create_tournaments_keyboard_editor(tournament_names):
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"tournament_out_bnt_{name}")]
        for name in tournament_names
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='edit_tournament')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок под ссылку турнира
async def get_links_tournaments(session: AsyncSession):
    end_date = datetime.today() - timedelta(days=3)
    result = await session.execute(
        select(Tournament.name_tournament, Tournament.link_table).where(
            func.str_to_date(Tournament.end_tournament, "%d.%m.%Y") >= end_date
        )
    )
    return {row[0]: row[1] for row in result.all()}


# Вывод кнопок под ссылку турнира, которые попали в архив
async def get_history_links_tournaments(session: AsyncSession):
    end_date = datetime.today() - timedelta(days=3)
    result = await session.execute(
        select(Tournament.name_tournament, Tournament.link_table).where(
            func.str_to_date(Tournament.end_tournament, "%d.%m.%Y") < end_date
        )
    )
    return {row[0]: row[1] for row in result.all()}


def create_links_tournaments_keyboard(tournaments_data):
    buttons = [
        [InlineKeyboardButton(text=name, url=link)]
        for name, link in tournaments_data.items()
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='tournament_table')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок под турнир для удаления участника
async def get_list_tournaments_players(session: AsyncSession):
    result = await session.execute(
        select(Tournament.name_tournament).where(
            func.str_to_date(Tournament.end_tournament, "%d.%m.%Y") >= datetime.today()
        )
    )
    return [f"{row[0]}_players" for row in result.all()]


def create_tournaments_keyboard_players(tournaments_data):
    buttons = [
        [InlineKeyboardButton(text=name.replace("_players", ""), callback_data=f"delete_player_{name}")]
        for name in tournaments_data
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок для редактирования турнира
async def get_list_tournaments_edit(session: AsyncSession):
    result = await session.execute(
        select(Tournament.name_tournament).where(
            func.str_to_date(Tournament.end_tournament, "%d.%m.%Y") >= datetime.today()
        )
    )
    return [f"{row[0]}_edit" for row in result.all()]


def create_tournaments_edit_keyboard(tournaments_data):
    buttons = [
        [InlineKeyboardButton(text=name.replace("_edit", ""), callback_data=f"tournament_edit_{name}")]
        for name in tournaments_data
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='edit_tournament')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок под учёт наличных расчётов за турнир
async def get_list_tournaments_players_kassa(session: AsyncSession):
    result = await session.execute(
        select(Tournament.name_tournament).where(
            func.str_to_date(Tournament.start_tournament, "%d.%m.%Y") >= datetime.today()
        )
    )
    return [f"{row[0]}_kassa" for row in result.all()]


def create_tournaments_keyboard_players_kassa(tournaments_data):
    buttons = [
        [InlineKeyboardButton(text=name.replace("_kassa", ""), callback_data=f"kassa_players_{name}")]
        for name in tournaments_data
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Вывод кнопок для удаления турнира
async def get_list_tournaments_delete(session: AsyncSession):
    result = await session.execute(
        select(Tournament.name_tournament).where(
            func.str_to_date(Tournament.end_tournament, "%d.%m.%Y") >= datetime.today()
        )
    )
    return [f"{row[0]}_delete" for row in result.all()]


def create_tournaments_delete_keyboard(tournaments_data):
    buttons = [
        [InlineKeyboardButton(text=name.replace("_delete", ""), callback_data=f"tournament_delete_{name}")]
        for name in tournaments_data
    ]
    buttons.append([InlineKeyboardButton(text='Назад', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Функция создания клавиатуры для уведомлений (не требует запроса к БД)
def create_tournaments_keyboard_notification(tournament_name):
    buttons = [
        [InlineKeyboardButton(text="Записаться! 🏆", callback_data=f"tournament_out_bnt_{tournament_name}")]
    ]
    buttons.append([InlineKeyboardButton(text='Главное меню!', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)