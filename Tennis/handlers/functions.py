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

from config.db import session
from models.User import User
from models.FastUser import FastUser
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers

router = Router()


MOSCOW_TZ = pytz.timezone("Europe/Moscow")

adm_start_t = "<b>Привет Хозяин!</b> 👋\n\nКак день?\nКак настроение?\n\nПротестируй весь мой функционал, чтобы я работал идеально! 👇"
m_edit_start_t = "Мы рады приветствовать тебя в команде нашего теннисного бота! Ваша роль крайне важна — благодаря вам турниры будут проходить гладко, а участники получат отличный игровой опыт.\n\n<b>Основные задачи:</b>\n\n✅ Распределение игроков по парам;\n✅ Анализ дивизиона для игроков;\n✅ Выдача банов\n\n🙋‍♂️ Если возникнут вопросы — пиши нам @sup_MM\n\n🔥 <b>Желаем ярких турниров и честной игры!</b>\n\n<b>С уважением, Мир – Новости</b>"
edit_start_t = "Мы рады приветствовать тебя в команде нашего теннисного бота! Ваша роль крайне важна — благодаря вам турниры будут проходить гладко, а участники получат отличный игровой опыт.\n\n<b>Основная задача:</b>\n\n✅ Создание и контроль турниров\n\n🙋‍♂️ Если возникнут вопросы — пиши нам @sup_MM\n\n🔥 <b>Желаем ярких турниров и честной игры!</b>\n\n<b>С уважением, Минск Мир – Новости</b>"
all_players_start_t = f"<b>Увлекаешься теннисом?</b> Давай расскажу, чем я 🤖 буду полезен тебе в ЖК \"Минск Мир\" 👇\n\n✅ Регистрирация на турнир;\n✅ Поиск соперников;\n✅ Бронирование корта;\n✅ Приобретение инвентаря\n\n💎 Для начала <b><a href='{CHANNEL}'>подпишитесь на канал</a>!</b> ⚡️ Здесь ты найдёшь актуальные новости, анонсы ярких мероприятий и обзоры заведений в Минск Мире!\n\n🙋‍♂️ Поддержка @sup_MM"


async def save_user(user_id, user_name, user_link): # Сохранение пользователей в список для рассылки

    user = session.query(User).filter_by(tg_user_id = user_id).first()
    if not user:
        print(f"Новый пользователь нажал /start")
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


# Вывод кнопоки для турнирной таблицы

def create_tournament_table_keyboard(user_id):
    last_toutnament_id = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == user_id).order_by(TournamentPlayers.id_tournament_players.desc()).first()    # протестировать на вывод последнего элемента
    
    if last_toutnament_id is None:
        buttons = [
            [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
            [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
            [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
            [InlineKeyboardButton(text = 'Барахолка 🛒', callback_data='inventory')]
        ]
    else:
        last_toutnament = session.query(Tournament).filter(Tournament.tournament_id == last_toutnament_id.id_tournament).first()

        buttons = [
            [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
            [InlineKeyboardButton(text = 'Турнирная таблица 📋', url=last_toutnament.link_table)],
            [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
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

        # Вычисляем следующее четверг 11:00
        days_until_thursday = (5 - now.weekday() + 7) % 7  # Суббота = 5-й день
        next_thursday = now + timedelta(days=days_until_thursday)
        target_time = next_thursday.replace(hour=11, minute=0, second=0, microsecond=0)

        wait_seconds = (target_time - now).total_seconds()
        # print(f"⏳ Ждём до {target_time.strftime('%d.%m.%Y %H:%M')}, осталось {wait_seconds:.2f} секунд")
        await asyncio.sleep(wait_seconds)  # Спим до субботы 11:00

        # Проверяем игроков
        users_without_division = session.query(User).filter(User.division_level.is_(None)).all()
        if len(users_without_division) > 1:
            for edit in MAIN_EDITOR:
                message_text_send = f"<b>⚠️ {len(users_without_division)} игрока(-ов) ожидают получения дивизиона!</b>"
                try:
                    await bot.send_message(chat_id=edit, text=message_text_send, parse_mode="HTML", reply_markup=ka.exit)
                    print("✅ Уведомление о игроках, ожидающих получение дивизиона, отправлено редактору!")
                except Exception as e:
                    print(f"❌ ОШИБКА: уведомление о игроках, ожидающих получение дивизиона, не было отправлено редактору ({edit}). Подробнее: {e}")

        # Ждём ровно 7 ДНЕЙ перед повторной проверкой
        await asyncio.sleep(604800)