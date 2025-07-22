import re
import os
import pytz
import asyncio
from sqlalchemy import null
from typing import Optional
from datetime import datetime
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError
from aiogram.types import CallbackQuery, LinkPreviewOptions, FSInputFile, Message
from aiogram import F, Router
from config.config import CHANNEL, CHANNELS_SUB, ADMINS, MAIN_EDITOR, EDITOR, DIVISION_EDITOR

import keywords.kw_start as kb
import keywords.kw_any as ka
import handlers.classes as cl
import handlers.validation as valid
import handlers.btn_tournaments as bt


from config.db_utils import get_db_readonly, get_db
from sqlalchemy import select
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
all_players_start_t = f"<b>Увлекаешься теннисом?</b> Давай расскажу, чем я 🤖 буду полезен тебе в ЖК \"Минск Мир\" 👇\n\n✅ Регистрация на турнир;\n✅ Поиск соперника;\n✅ Бронирование корта;\n✅ Приобретение инвентаря\n\n💎 Следи за телеграмм каналом <b><a href='{CHANNEL}'>Минск-Мир - Новости</a>!</b> ⚡️ Здесь ты найдёшь актуальные новости, анонсы ярких мероприятий и обзоры заведений в Минск Мире!\n\n🙋‍♂️ Поддержка @sup_MM"


async def save_user(user_id, user_name, user_link, message, state:FSMContext): # Сохранение пользователей в список для рассылки
    async with get_db() as session:  # Используем контекстный менеджер

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if not user:
            print(f"Новый пользователь нажал /start")

            # СКАЗКА (~30 секунд)

            story = await message.answer(f"Привет <b>{user_name}!</b> 👋", parse_mode=ParseMode.HTML)  # Сохраняем отправленное сообщение
            await asyncio.sleep(2)
            await story.edit_text("Давай я расскажу тебе 1 историю... 🎾")
            await asyncio.sleep(2.5)
            await story.edit_text("Где-то в далёком-придалёком королевстве 👑")
            await asyncio.sleep(2.5)
            await story.edit_text("Среди замков и драконов 🐉")
            await asyncio.sleep(1.9)
            await story.edit_text("Основался легендарный теннисный клуб! 🛡️")
            await asyncio.sleep(2.5)
            await story.edit_text("Только самые смелые выходили на корт ⚡️")
            await asyncio.sleep(2.5)
            await story.edit_text("Их ждали великие дуэли, турниры и таинственные награды...")
            await asyncio.sleep(3)
            await story.edit_text("Хочешь очутиться в далёком-придалёком королевстве? 👑")
            await asyncio.sleep(2.8)
            await story.edit_text("Сразиться с соперниками?!")
            await asyncio.sleep(2)
            await story.edit_text("Выиграть турнир?! 🏆")
            await asyncio.sleep(2)
            await story.edit_text("Стать теннисным лордом?! 👑")
            await asyncio.sleep(2.1)
            await story.edit_text("<b>Пора начинать наше приключение!</b> 🚀", parse_mode=ParseMode.HTML)
            await asyncio.sleep(2.3)
            await story.edit_text("Корт ждёт героя, готового вписать своё имя в историю! 🎾")
            await asyncio.sleep(3)
            await story.delete()

            old_user = (await session.scalars(select(OldUsers).where(OldUsers.tg_old_users_id == user_id))).first()

            if old_user:
                new_user = User(tg_user_id = user_id, name_user = user_name, link = user_link, division_level = old_user.division_level)
            else:
                new_user = User(tg_user_id = user_id, name_user = user_name, link = user_link)

            session.add(new_user)

            await state.update_data(user_id_skill = user_id)
            await state.set_state(cl.SendSkill.name)
            await message.answer('<b>Давай знакомиться!</b>\n\nЯ - 🤖 Бот по теннису. \nНапиши своё полное Имя и Фамилию 👇', parse_mode=ParseMode.HTML)
    
        else:

            options = LinkPreviewOptions(
                url=CHANNEL,
                prefer_small_media=True
            )
                
            if user_id in ADMINS:
                await message.answer(adm_start_t, parse_mode=ParseMode.HTML, reply_markup=kb.main_admin_btn)
            elif user_id in MAIN_EDITOR:
                await message.answer(f"<b>Уважаемый {user_name}!</b> 👋\n\n{m_edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.main_edit_btn)
            elif user_id in EDITOR:
                await message.answer(f"<b>Уважаемый {user_name}!</b> 👋\n\n{edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.edit_btn)
            else:
                keyboard = await create_tournament_table_keyboard_user(user_id)
                await message.answer(f"<b>Привет {user_name}!</b> 👋\n\n{all_players_start_t}", parse_mode=ParseMode.HTML, link_preview_options=options, reply_markup=keyboard)



@router.message(cl.SendSkill.name)
async def register_name(message: Message, state:FSMContext):
    user_name = message.text.strip()
    # Проверяем, корректно ли введен текст
    if not valid.validate_name(user_name):
        remaining_chars = len(user_name) - 64
        await message.answer(f"⚠ Ошибка! Длина ответа превышена на {remaining_chars} символов. Попробуйте снова 👇")
        return  # Останавливаем обработку, чтобы пользователь ввел данные снова

    # Проверяем, корректно ли введен текст
    if not valid.validate_start(user_name):
        await message.answer(f"⚠ Ошибка! Имя и Фамилия не могут быть /start. Попробуйте снова 👇")
        return  # Останавливаем обработку, чтобы пользователь ввел данные снова

    await state.update_data(name_skill = message.text)
    await state.set_state(None)
    
    await state.set_state(cl.SendSkill.skill)
    await message.answer('<b>Для определения твоего уровня игры, ответь одним сообщением на несколько вопросов</b> 👇\n\n1. Сколько лет/месяцев в теннисе?\n2. Был ли опыт каких-то турниров до этого? (если играл только в Raketo, укажи сколько матчей и какой рейтинг)\n3. Занимался ли когда-то с тренером?\n4. Играл ли против кого-то из наших игроков, если да - то как сыграли?', parse_mode=ParseMode.HTML)



@router.message(cl.SendSkill.skill)
async def register_skill(message: Message, state:FSMContext, bot):
    user_skill = message.text.strip()
    data = await state.get_data()

    # Проверяем, корректно ли введен текст
    if not valid.validate_comment(user_skill):
        remaining_chars = len(user_skill) - 300
        await message.answer(f"⚠ Ошибка! Длина ответа превышена на {remaining_chars} символов. Попробуйте снова 👇")
        return  # Останавливаем обработку, чтобы пользователь ввел данные снова
    
    # Проверяем, корректно ли введен текст
    if not valid.validate_start(user_skill):
        await message.answer(f"⚠ Ошибка! Ответ не может быть /start. Попробуйте снова 👇")
        return  # Останавливаем обработку, чтобы пользователь ввел данные снова

    await state.set_state(None)

    async with get_db() as session:  # Используем контекстный менеджер

        user = (await session.scalars(select(User).where(User.tg_user_id == data.get("user_id_skill")))).first()
        
        if user:
            user.name_user = data.get("name_skill")
            user.skill = user_skill

    await state.clear()
    
    user_name = message.from_user.full_name if message.from_user.username else message.from_user.username
    user_id = message.from_user.id

    options = LinkPreviewOptions(
        is_disabled=True
    )

    if user_id in ADMINS:
        await message.answer(adm_start_t, parse_mode=ParseMode.HTML, reply_markup=kb.main_admin_btn)
    elif user_id in MAIN_EDITOR:
        await message.answer(f"<b>Уважаемый {user_name}!</b> 👋\n\n{m_edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.main_edit_btn)
    elif user_id in EDITOR:
        await message.answer(f"<b>Уважаемый {user_name}!</b> 👋\n\n{edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.edit_btn)
    else:
        keyboard = await create_tournament_table_keyboard_user(user_id)
        await message.answer(f"<b>Привет {user_name}!</b> 👋\n\n{all_players_start_t}", link_preview_options=options, disable_web_page_preview=True, parse_mode=ParseMode.HTML, reply_markup=keyboard)



async def check_subscription(user_id: int, bot) -> bool: # Проверяет, подписан ли пользователь на канал
    try:
        for channel in CHANNELS_SUB:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False  # Не подписан на текущий канал
        return True  # Подписан на все каналы
    except TelegramBadRequest:
        return False
    

    
async def check_subscription_message(callback: CallbackQuery):
    user_name = callback.from_user.full_name if callback.from_user.username else callback.from_user.username
    await callback.message.answer(f"<b>{user_name}</b>, даю слово, я 🤖 буду помогать тебе до последнего вздоха, но для продолжения <b>подпишись на наш канал</b> 👇", parse_mode=ParseMode.HTML, reply_markup=kb.builder)



async def check_fast_user(user_id, session: AsyncSession):
    user_fast = (await session.scalars(select(FastUser).where(FastUser.tg_id_user == user_id))).first()
    
    if user_fast:
        return True
    else:
        return False 
    


async def check_ban_user(user_id, session: AsyncSession):
    user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
    
    if user.ban_status:
        end_date = datetime.strptime(user.end_date_ban, "%d.%m.%Y")

        if datetime.today() > end_date:        
            user.end_date_ban = None
            user.ban_status = None




@router.callback_query(F.data == 'start_message')
async def start_message(callback: Optional[CallbackQuery] = None, message: Optional[Message] = None, bot = None):
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
        keyboard = await create_tournament_table_keyboard_user(user_id)
        await callback.message.answer(f"<b>Привет {user_name}!</b> 👋\n\n{all_players_start_t}", link_preview_options=options, disable_web_page_preview=True, parse_mode=ParseMode.HTML, reply_markup=keyboard)


# Вывод кнопок для user

async def create_tournament_table_keyboard_user(user_id):
    async with get_db_readonly() as session:  # Используем контекстный менеджер
        last_tournament = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == user_id).order_by(TournamentPlayers.id_tournament_players.desc()))).first()

    if str(user_id) == DIVISION_EDITOR:
        if last_tournament is None:
            buttons = [
                [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
                [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='match')],
                [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                [InlineKeyboardButton(text = 'Турнирные таблицы 📋', callback_data='tournament_table')],
                [InlineKeyboardButton(text = 'Установить дивизион 🥇', callback_data='set_division')],
                [InlineKeyboardButton(text = 'Барахолка 🛒', callback_data='inventory')] # запятая
                # [InlineKeyboardButton(text = 'Реферальная система 👥', callback_data='referral_system')]
            ]
        else:
            buttons = [
                [InlineKeyboardButton(text = 'Турнир 🏆', callback_data='user_tournament_keyboard')],
                [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='match')],
                [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                [InlineKeyboardButton(text = 'Установить дивизион 🥇', callback_data='set_division')],
                [InlineKeyboardButton(text = 'Барахолка 🛒', callback_data='inventory')] # запятая
                # [InlineKeyboardButton(text = 'Реферальная система 👥', callback_data='referral_system')]
            ]
    else:
        if last_tournament is None:
            buttons = [
                [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
                [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='match')],
                [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                [InlineKeyboardButton(text = 'Турнирные таблицы 📋', callback_data='tournament_table')],
                [InlineKeyboardButton(text = 'Барахолка 🛒', callback_data='inventory')] # запятая
                # [InlineKeyboardButton(text = 'Реферальная система 👥', callback_data='referral_system')]
            ]
        else:
            buttons = [
                [InlineKeyboardButton(text = 'Турнир 🏆', callback_data='user_tournament_keyboard')],
                [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='match')],
                [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                [InlineKeyboardButton(text = 'Барахолка 🛒', callback_data='inventory')] # запятая
                # [InlineKeyboardButton(text = 'Реферальная система 👥', callback_data='referral_system')]
            ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == 'user_tournament_keyboard')
async def user_tournament_keyboard(callback: CallbackQuery):
    await callback.answer('')

    async with get_db_readonly() as session:  # Используем контекстный менеджер

        user_id = callback.from_user.id

        last_tournament_id = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == user_id).order_by(TournamentPlayers.id_tournament_players.desc()))).first()
        
        if last_tournament_id is not None:
            last_tournament = (await session.scalars(select(Tournament).where(Tournament.tournament_id == last_tournament_id.id_tournament))).first()

            link_table = last_tournament.link_table
            keyboard = await create_tournament_table_keyboard(link_table)
            
            if os.path.exists(f"Tennis/img/tournament/{last_tournament.tournament_id}.jpg"):
                pyth_photo = f"Tennis/img/tournament/{last_tournament.tournament_id}.jpg"
                
                photo = FSInputFile(pyth_photo)
                await callback.message.answer_photo(photo, caption=f"<b>Тут собрана вся полезная информация касающаяся турнира</b>, в котором Вы участвуете! 🏆\n\n😎 \"Только упорные тренировки сделают из тебя чемпиона!\"", parse_mode=ParseMode.HTML, reply_markup=keyboard)
            
            else:
                await callback.message.answer(f"<b>Тут собрана вся полезная информация касающаяся турнира</b>, в котором Вы участвуете! 🏆\n\n😎 \"Только упорные тренировки сделают из тебя чемпиона!\"", parse_mode=ParseMode.HTML, reply_markup=keyboard)


async def create_tournament_table_keyboard(link_table):

    buttons = [
        [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data = 'tournament_info')],
        [InlineKeyboardButton(text = 'Турнирная таблица 📋', url = link_table)],
        [InlineKeyboardButton(text = 'Записать счёт 🙋‍♂️', callback_data = 'score')],
        [InlineKeyboardButton(text = 'Назад', callback_data = 'start_message')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)



async def output_edits_list(session: AsyncSession):
    edits = (await session.scalars(select(User).where(User.tg_user_id.in_(EDITOR)))).all()
    
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
        async with get_db_readonly() as session:  # Используем контекстный менеджер
            users_without_division = (await session.scalars(select(User).where(User.division_level.is_(None)))).all()
        
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



async def notification_about_new_tournament(tournament_name, tournament_start, division, bot, session: AsyncSession): # находим игроков, хоть раз участвовавших в турнирах для отправки уведомления о создании нового турнира
    users = (await session.scalars(select(User).where(User.division_level.in_(division.split(','))))).all()
    
    if users:
        users_tg_ids = [user.tg_user_id for user in users]
        players = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user.in_(users_tg_ids)))).all()
        
        if players:
            players_tg_ids = [player.id_tg_user for player in players]

            if players_tg_ids:
                try:
                    message_text_send = f"⚡️ <b>Доступен новый турнир для вашего дивизиона!</b>\n\n<b>Название:</b> {tournament_name}\n<b>Дата начала:</b> {tournament_start}\n\n<b>Хотите принять участие? 😎</b>"
                    exit = bt.create_tournaments_keyboard_notification(tournament_name)
                    for players_tg_id in list(set(players_tg_ids)):
                        await bot.send_message(chat_id=players_tg_id, text=message_text_send, parse_mode=ParseMode.HTML, reply_markup=exit)
                except Exception as e:
                    print(f"❌ Не удалось отправить сообщение о появлении нового турнира пользователю с id: {players_tg_id} из-за ошибки: {e}")



@router.callback_query(F.data == 'spam')
async def spam(callback: CallbackQuery, bot):

    await callback.answer(f"Спасибо за обращение!", show_alert=False)

    message_text = callback.message.text
    match = re.search(r"(@[^\s]+) vs (@[^\s]+)\n.*? Счёт: ([\d: ]+)", message_text)  # Ищем нужные значения

    if match:
        spam_name = match.group(1)  # Спамер
        user_name = match.group(2)  # Игрок
        text = match.group(3)  # Игрок

        message_text_send = f"<b>Игрок {user_name} подал заявку о спаме на пользователя {spam_name} ❗️</b>\n\nТекст сообщения: {text}"
        for admin in ADMINS:
            try:
                await bot.send_message(chat_id=admin, text=message_text_send, parse_mode=ParseMode.HTML, reply_markup=ka.exit)
            except Exception as e:
                print(f"❌ Не удалось отправить сообщение от пользователя {user_name} из-за ошибки: {e}")
    else:
        print(f"❌ Сообщение о СПАМе не дошло от пользователя {user_name} из-за ошибки: {e}")

    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()



