import re
import pytz
import dateparser
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from datetime import datetime, timedelta
from aiogram.enums import ParseMode
from typing import Optional

import keywords.kw_user as kb
import keywords.kw_any as ka
import handlers.classes as cl
import handlers.functions as f
import handlers.validation as valid

from config.db_utils import get_db_readonly, get_db
from sqlalchemy import select
from models.User import User
from models.Match import Match

router = Router()

user_data = {}  # Ключ: username, значение: PlayerData
MOSCOW_TZ = pytz.timezone('Europe/Moscow')


@router.callback_query(F.data == 'register_player')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    async with get_db_readonly() as session:  # Используем контекстный менеджер

        user_id = callback.from_user.id
        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if user:
            if user.age and user.sex:
                await callback.message.answer('Вы уже забронировали корт? 🎾', reply_markup=kb.booking_court_q)
            elif user.age:
                await state.set_state(cl.RegPlayerStates.sex)
                await callback.message.answer('Выберите ваш пол 👇', reply_markup=kb.sex)
            else:
                await state.set_state(cl.RegPlayerStates.age)
                await callback.message.answer('Введите ваш возраст 👇')
        else:
            await state.set_state(cl.RegPlayerStates.age)
            await callback.message.answer('Введите ваш возраст 👇')



@router.message(cl.RegPlayerStates.age)
async def register_age(message: Message, state:FSMContext):
    user_age = message.text.strip()

    # Проверяем, корректно ли введен возраст
    if not valid.validate_age(user_age):
        await message.answer("⚠ Ошибка! Введите <b>целое положительное число</b>. Попробуйте снова 👇", parse_mode=ParseMode.HTML)
        return  # Останавливаем обработку, чтобы пользователь ввел данные снова
    
    await state.set_state(None)

    await state.update_data(age = message.text)
    await message.answer('Выберите Ваш пол 👇', reply_markup=kb.sex)



@router.callback_query(F.data.in_(["men", "women"]))
async def register_sex(call: CallbackQuery, state: FSMContext):
    await call.answer('')
    if call.data == "men":
        await state.update_data(sex = 'Мужчина')
    elif call.data == "women":
        await state.update_data(sex = 'Женщина')
    await call.message.answer('Вы уже забронировали корт? 🎾', reply_markup=kb.booking_court_q)



@router.callback_query(F.data.in_(["yes_b_c", "no_b_c"]))
async def register_date_q(call: CallbackQuery, state: FSMContext):
    await call.answer('')
    if call.data == "yes_b_c":
        await call.message.answer('Выберите забронированный корт 👇', reply_markup=ka.name_booking_court)
    elif call.data == "no_b_c":
        await state.set_state(cl.RegPlayerStates.date_without_booking)
        await call.message.answer(f'<b>Укажите дату!</b> 🔥 Просто напишите дату и время так, как вам удобно!\n\n<b>Вот несколько примеров 👇</b>\n<blockquote>- "завтра в 18:00"\n- "воскресенье, 3 часа дня"\n- "25 декабря, 19:00"\n- "через 2 недели в 10 утра"\n- "14:00, 5 октября"\n- "10 июня 2025 года 14:30"</blockquote>', parse_mode=ParseMode.HTML) 



@router.callback_query(F.data.in_(["name_court_1", "name_court_2", "name_court_3", "name_court_4", "name_court_5", "name_court_6"]))
async def register_date_q(call: CallbackQuery, state: FSMContext):
    await call.answer('')
    if call.data == "name_court_1":
        await state.update_data(name_court = 'Северная Америка - Кижеватова 3Б')
    if call.data == "name_court_2":
        await state.update_data(name_court = 'Африка - Теслы 6')
    if call.data == "name_court_3":
        await state.update_data(name_court = 'Центральная Европа - Теслы 16')
    if call.data == "name_court_4":
        await state.update_data(name_court = 'Средиземноморский - Теслы 24')
    if call.data == "name_court_5":
        await state.update_data(name_court = 'Тропические острова - Лученка 24')
    if call.data == "name_court_6":
        await state.update_data(name_court = 'Евразия - Лученка 1')

    await state.set_state(cl.RegPlayerStates.date_booking)
    await call.message.answer(f'<b>Укажите дату 👇</b> \n\n🔥 Просто напишите дату и время так, как вам удобно!\n\n<b>Вот несколько примеров 👇</b>\n<blockquote>- "завтра в 18:00"\n- "воскресенье, 3 часа дня"\n- "25 декабря, 19:00"\n- "через 2 недели в 10 утра"\n- "14:00, 5 октября"\n- "10 июня 2025 года 14:30"</blockquote>', parse_mode=ParseMode.HTML) 



@router.message(cl.RegPlayerStates.date_booking)
async def register_date(message: Message, state:FSMContext):
    user_id = message.from_user.id
    user = message.from_user

    if user.username:
        user_link = f"https://t.me/{user.username}"
    else:
        user_link = ""
    
    await state.update_data(user_id = user_id)
    await state.update_data(link = user_link)

    user_date = message.text.strip()

    date = dateparser.parse(user_date, languages=['ru'], settings={'TIMEZONE': 'Europe/Moscow', 'TO_TIMEZONE': 'Europe/Moscow'})
    if not date:
        await message.reply("⚠ Не понял дату, попробуйте ещё раз 👇")
        return # Останавливаем обработку
    else:
        date_str = date.strftime("%H:%M %d.%m.%Y")
        await state.set_state(None)
        await state.update_data(date_booking = date_str)

        await message.answer('Укажите тип игры 👇', reply_markup=kb.type_match)



@router.message(cl.RegPlayerStates.date_without_booking)
async def register_date(message: Message, state:FSMContext):
    user_id = message.from_user.id
    user = message.from_user

    if user.username:
        user_link = f"https://t.me/{user.username}"
    else:
        user_link = ""
    
    await state.update_data(user_id = user_id)
    await state.update_data(link = user_link)

    user_date = message.text.strip()

    date = dateparser.parse(user_date, languages=['ru'], settings={'TIMEZONE': 'Europe/Moscow', 'TO_TIMEZONE': 'Europe/Moscow'})
    if not date:
        await message.reply("⚠ Не понял дату, попробуйте ещё раз 👇")
        return # Останавливаем обработку
    else:
        date_str = date.strftime("%H:%M %d.%m.%Y")
        await state.set_state(None)
        await state.update_data(date_without_booking = date_str)

        await message.answer('Укажите тип игры 👇', reply_markup=kb.type_match)



@router.callback_query(F.data.in_(["type_match_1", "type_match_2"]))
async def type_match(call: CallbackQuery, state: FSMContext):
    await call.answer('')
    if call.data == "type_match_1":
        await state.update_data(type_match = 'Одиночный')
        await call.message.answer('Хотите оставить комментарий?', reply_markup=kb.comment_q)

    elif call.data == "type_match_2":
        await state.update_data(type_match = 'Парный')
        await call.message.answer('Хотите оставить комментарий?', reply_markup=kb.comment_q)



@router.callback_query(F.data.in_(["yes_c", "no_c"]))
async def register_comment_q(call: CallbackQuery, state: FSMContext):
    await call.answer('')
    if call.data == "yes_c":
        await state.set_state(cl.RegPlayerStates.comment)
        await call.message.answer(f'Укажите комментарий 👇') 

    if call.data == "no_c":
        await state.update_data(comment = None)
        await register_card(None, call.message, state)



@router.message(cl.RegPlayerStates.comment)
async def register_comment(message: Message, state: FSMContext):
    user_comment = message.text.strip()

    if not valid.validate_comment(user_comment):
        remaining_chars = len(user_comment) - 300
        await message.answer(f"⚠ Ошибка! Длина комментария превышена на {remaining_chars} символов. Попробуйте снова 👇")
        return  # Останавливаем обработку
    
    await state.set_state(None)
    
    await state.update_data(comment = message.text)
    await register_card(None, message, state)



async def register_card(callback: Optional[CallbackQuery], message: Message, state: FSMContext):
    data = await state.get_data()
    async with get_db() as session:  # Используем контекстный менеджер

        # Создаём объект PlayerData
        player_data = cl.PlayerData(
            id=data.get("user_id"),
            link=data.get("link"),
            age=data.get("age"),
            sex=data.get("sex"),
            date_booking=data.get("date_booking"),
            date_without_booking=data.get("date_without_booking"),
            name_court=data.get("name_court"),
            type_match=data.get("type_match"),
            comment=data.get("comment")
        )

        new_match = Match(id_tg_user = data.get("user_id"), date_booking = data.get("date_booking"), date_without_booking = data.get("date_without_booking"), name_court = data.get("name_court"), type = data.get("type_match"), comment = data.get("comment"), player_1 = data.get("user_id"))
        session.add(new_match)
        user = (await session.scalars(select(User).where(User.tg_user_id == data.get("user_id")))).first()
        user.age = data.get("age")
        user.sex = data.get("sex")

    print(f'✅ Карточка игры создана пользователем с ID {data.get("user_id")}!')
    if callback:
        await callback.message.answer('✅ Игра создана!')
    else:
        await message.answer('✅ Игра создана!')

    async with get_db() as session:  # Используем контекстный менеджер
        await f.check_ban_user(data.get("user_id"), session)

    if callback:
        await callback.message.answer(f'<b>Ваша карточка игры выглядит так</b> 👇\n\n{(await player_data.build_text_card())}', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.player)
    else:
        await message.answer(f'<b>Ваша карточка игры выглядит так</b> 👇\n\n{(await player_data.build_text_card())}', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.player)

    # Обнуляем данные
    await state.update_data(date_booking = None)
    await state.update_data(date_without_booking = None)



@router.callback_query(F.data == 'match_requests')
async def match_requests(callback: CallbackQuery):
    await callback.answer('')

    user_id = callback.from_user.id

    async with get_db() as session:  # Используем контекстный менеджер
        await f.check_ban_user(user_id, session)

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
        user_matches = (await session.scalars(select(Match).where((Match.id_tg_user == user_id) & (Match.player_2 == None)))).all()

    if user_matches:
        if len(user_matches) == 1:
            await callback.message.answer(f'<b>Ваш запрос на игру выглядит так</b> 👇', parse_mode=ParseMode.HTML)
        else:
            await callback.message.answer(f'<b>Ваши запросы на игры выглядят так</b> 👇', parse_mode=ParseMode.HTML)

        for user_match in user_matches:
            if user and user_match:
                text = ''

                if user_match.date_booking:
                    text += f'\n\n✅ <b>Бронь корта:</b> {user_match.date_booking}\n<b>Корт:</b> {user_match.name_court}'
                    
                if user_match.date_without_booking:
                    text += f'\n\n❌ <b>Брони нет! Предлагаю поиграть:</b> {user_match.date_without_booking}'
                
                if user_match.type:
                    text += f'\n<b>Тип игры:</b> {user_match.type}'
                
                if user_match.comment:
                    text += f'\n<b>Комментарий:</b> <blockquote>{user_match.comment}</blockquote>'
                
                await callback.message.answer(f'<b>Запрос на игру</b> (ID: {user_match.match_id}) 🎾\n\n{(await user.build_repr_data())}{text}', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.player_get_card)
        if len(user_matches) < 3:
                await callback.message.answer(f'<b>Хотите создать ещё 1 запрос на игру?</b>', parse_mode=ParseMode.HTML, reply_markup=kb.add_card_q)
    else:
        await callback.message.answer("<b>Активных игр не найдено! Хотите создать?</b>", parse_mode=ParseMode.HTML, reply_markup=kb.create_card)



@router.callback_query(F.data == 'delete_match')
async def delete_match(callback: types.CallbackQuery, state: FSMContext):

    user_id = callback.from_user.id
    
    message_text = callback.message.text or callback.message.caption  # Получаем текст сообщения
    match = re.search(r"ID: (\d+)", message_text)  # Ищем нужные значения

    if match:
        match_id = match.group(1)       # ID карточки
        
        async with get_db() as session:  # Используем контекстный менеджер

            user_match = (await session.scalars(select(Match).where(Match.match_id == match_id))).first()
            
            if user_match:
                try:
                    await session.delete(user_match)
                    await callback.answer(f"✅ Карточка удалена!", show_alert=False)
                except Exception as e:
                    # обработка ошибки
                    print(f"Произошла ошибка: {e}")    
    else:
        print("❌ При попытке удалить карточку игры произошла ошибка!")

    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()