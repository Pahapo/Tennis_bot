import asyncio
from datetime import datetime, timedelta
import pytz
from sqlalchemy import null
from datetime import datetime
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram import F, Router
from config.config import CHANNEL, CHANNEL_ID, ADMINS, MAIN_EDITOR, EDITOR

import keywords.kw_start as kb
import keywords.kw_any as ka
import handlers.btn_tournaments as bt

from config.db import session
from models.User import User
from models.OldUsers import OldUsers
from models.FastUser import FastUser
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers

router = Router()


MOSCOW_TZ = pytz.timezone("Europe/Moscow")

adm_start_t = "<b>Привет Хозяин!</b> 👋\n\nКак день?\nКак настроение?\n\nПротестируй весь мой функционал, чтобы я работал идеально! 👇"
m_edit_start_t = "Мы рады приветствовать тебя в команде нашего теннисного бота! Ваша роль крайне важна — благодаря вам турниры будут проходить гладко, а участники получат отличный игровой опыт.\n\n<b>Основные задачи:</b>\n\n✅ Распределение игроков по парам;\n✅ Анализ дивизиона для игроков;\n✅ Выдача банов\n\n🙋‍♂️ Если возникнут вопросы — пиши нам @sup_MM\n\n🔥 <b>Желаем ярких турниров и честной игры!</b>\n\n<b>С уважением, Мир – Новости</b>"
edit_start_t = "Мы рады приветствовать тебя в команде нашего теннисного бота! Ваша роль крайне важна — благодаря вам турниры будут проходить гладко, а участники получат отличный игровой опыт.\n\n<b>Основная задача:</b>\n\n✅ Создание и контроль турниров\n\n🙋‍♂️ Если возникнут вопросы — пиши нам @sup_MM\n\n🔥 <b>Желаем ярких турниров и честной игры!</b>\n\n<b>С уважением, Минск Мир – Новости</b>"
all_players_start_t = f"<b>Увлекаешься теннисом?</b> Давай расскажу, чем я 🤖 буду полезен тебе в ЖК \"Минск Мир\" 👇\n\n✅ Регистрирация на турнир;\n✅ Поиск соперника;\n✅ Бронирование корта;\n✅ Приобретение инвентаря\n\n💎 Следи за телеграмм каналом <b><a href='{CHANNEL}'>Минск-Мир - Новости</a>!</b> ⚡️ Здесь ты найдёшь актуальные новости, анонсы ярких мероприятий и обзоры заведений в Минск Мире!\n\n🙋‍♂️ Поддержка @sup_MM"


async def save_user(user_id, user_name, user_link): # Сохранение пользователей в список для рассылки

    user = session.query(User).filter(User.tg_user_id == user_id).first()
    if not user:
        print(f"Новый пользователь нажал /start")

        old_user = session.query(OldUsers).filter(OldUsers.tg_old_users_id == user_id).first()

        if old_user:
            new_user = User(tg_user_id = user_id, name_user = user_name, link = user_link, division_level = old_user.division_level)
        else:
            new_user = User(tg_user_id = user_id, name_user = user_name, link = user_link)

        session.add(new_user)
        session.commit() # Сохраняем изменения (фиксируем транзакцию)

    



async def check_subscription(user_id: int, bot) -> bool: # Проверяет, подписан ли пользователь на канал
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramBadRequest:
        return False
    

    
async def check_subscription_message(callback: CallbackQuery):
    user_name = callback.from_user.full_name if callback.from_user.username else callback.from_user.username
    await callback.message.answer(f"<b>{user_name}</b>, даю слово, я 🤖 буду помогать тебе до последнего вздоха, но для продолжения <b>подпишись на наш канал</b> 👇", parse_mode=ParseMode.HTML, reply_markup=kb.builder)



async def check_fast_user(user_id):
    user_fast = session.query(FastUser).filter(FastUser.tg_id_user == user_id).first()
    if user_fast:
        return True
    else:
        return False 



async def check_ban_user(user_id):
    user = session.query(User).filter_by(tg_user_id = user_id).first()
    if user.ban_status:
        end_date = datetime.strptime(user.end_date_ban, "%d.%m.%Y")

        if datetime.today() > end_date:
            user.end_date_ban = None
            user.ban_status = None
            session.commit() # Сохраняем изменения (фиксируем транзакцию)



@router.callback_query(F.data == 'start_message')
async def start_message(callback: CallbackQuery, bot):
    await callback.answer('')

    user_name = callback.from_user.full_name if callback.from_user.username else callback.from_user.username
    user_id = callback.from_user.id

    options = LinkPreviewOptions(
        is_disabled=True
    )

    if user_id in ADMINS:
        await callback.message.answer(adm_start_t, parse_mode=ParseMode.HTML, reply_markup=kb.main_admin_btn)
    elif user_id in MAIN_EDITOR:
        await callback.message.answer(f"<b>Уважаемый {user_name}!</b> 👋\n\n{m_edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.main_edit_btn)
    elif user_id in EDITOR:
        await callback.message.answer(f"<b>Уважаемый {user_name}!</b> 👋\n\n{edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.edit_btn)
    else:
        await callback.message.answer(f"<b>Привет {user_name}!</b> 👋\n\n{all_players_start_t}", link_preview_options=options, disable_web_page_preview=True, parse_mode=ParseMode.HTML, reply_markup=create_tournament_table_keyboard(user_id))



# Вывод кнопоки для user

def create_tournament_table_keyboard(user_id):
    last_toutnament_id = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == user_id).order_by(TournamentPlayers.id_tournament_players.desc()).first()    # протестировать на вывод последнего элемента
    
    if last_toutnament_id is None:
        buttons = [
            [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
            [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='match')],
            [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
            [InlineKeyboardButton(text = 'Барахолка 🛒', callback_data='inventory')]
        ]
    else:
        last_toutnament = session.query(Tournament).filter(Tournament.tournament_id == last_toutnament_id.id_tournament).first()

        buttons = [
            [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
            [InlineKeyboardButton(text = 'Турнирная таблица 📋', url=last_toutnament.link_table)],
            [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='match')],
            [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
            [InlineKeyboardButton(text = 'Барахолка 🛒', callback_data='inventory')]
        ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)



async def output_edits_list():
    edits = session.query(User).filter(User.tg_user_id.in_(EDITOR)).all() # Получаем список User с указанным free_time
    edit_list = ''
    for edit in edits:
        edit_list += f"\n🙋‍♂️ <a href='{edit.link}'>{edit.name_user}</a>"
    return edit_list    



async def check_players(bot):
    while True:
        now = datetime.now(tz=MOSCOW_TZ)

        # Определяем, сколько дней до следующего вторника или субботы
        if now.weekday() < 1:  # Сегодня понедельник или ранее — ждем вторника
            days_until_target = (1 - now.weekday()) % 7
        else:  # Сегодня вторник или позже — ждем субботы
            days_until_target = (6 - now.weekday()) % 7

        next_target_day = now + timedelta(days=days_until_target)
        target_time = next_target_day.replace(hour=11, minute=0, second=0, microsecond=0)

        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)  # Спим до нужного дня

        # Проверяем игроков
        users_without_division = session.query(User).filter(User.division_level.is_(None)).all()
        if len(users_without_division) > 1:
            for edit in MAIN_EDITOR:
                message_text_send = f"<b>⚠️ {len(users_without_division)} игрока(-ов) ожидают получения дивизиона!</b>"
                try:
                    await bot.send_message(chat_id=edit, text=message_text_send, parse_mode="HTML", reply_markup=ka.exit)
                    print(f"✅ Уведомление отправлено ({edit})!")
                except Exception as e:
                    print(f"❌ Ошибка: {e}")

        # Ждем 3 или 4 дня до следующей проверки
        await asyncio.sleep(259200 if now.weekday() == 1 else 345600)  # 3 дня до субботы, 4 до вторника



async def notification_about_new_tournament(tournament_name, tournament_start, division, bot): # находим игроков, хоть раз участвовавших в турнирах для отправки уведомления о создании нового турнира
    users = session.query(User).filter(User.division_level.in_(division.split(','))).all()
    if users:
        users_tg_ids = [user.tg_user_id for user in users]
        players = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user.in_(users_tg_ids)).all()
        if players:
            players_tg_ids = [player.id_tg_user for player in players]

            if players_tg_ids:
                try:
                    message_text_send = f"⚡️ <b>Доступен новый турнир для вашего дивизиона!</b>\n\n<b>Название:</b> {tournament_name}\n<b>Дата начала:</b> {tournament_start}\n\n<b>Хотите принять участие? 😎</b>"
                    exit = bt.create_tournaments_keyboard_notification(tournament_name)
                    for players_tg_id in list(set(players_tg_ids)):
                        await bot.send_message(chat_id=players_tg_id, text=message_text_send, parse_mode=ParseMode.HTML, reply_markup=exit)
                except Exception as e:
                    print(f"Не удалось отправить сообщение о появлении нового турнира пользователю с id: {players_tg_id} из-за ошибки: {e}")
