import re
import pytz
from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from datetime import datetime
from typing import Optional

import keywords.kw_user as kb
import handlers.classes as cl
import handlers.functions as f

from config.db import session
from models.User import User
from models.Match import Match

router = Router()

user_data = {}  # Ключ: username, значение: PlayerData


@router.callback_query(F.data == 'register_player')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')

    data = await state.get_data()
    user_id = data.get("user_id")
    user = session.query(User).filter(User.tg_user_id == user_id).first()

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
    user_id = message.from_user.id
    user = message.from_user

    if user.username:
        user_link = f"https://t.me/{user.username}"
    else:
        user_link = ""
        
    await state.update_data(id = user_id)
    await state.update_data(link = user_link)
    await state.update_data(age = message.text)
    await message.answer('Выберите ваш пол 👇', reply_markup=kb.sex)



@router.callback_query(F.data.in_(["men", "women"]))
async def register_sex(call: CallbackQuery, state: FSMContext):
    await call.answer('')
    if call.data == "men":
        await state.update_data(sex = 'Мужчина')
    if call.data == "women":
        await state.update_data(sex = 'Женщина')
    await state.set_state(cl.RegPlayerStates.booking)
    await call.message.answer('Вы уже забронировали корт? 🎾', reply_markup=kb.booking_court_q)



@router.callback_query(F.data.in_(["yes_b_c", "no_b_c"]))
async def register_date_q(call: CallbackQuery, state: FSMContext):
    await call.answer('')
    if call.data == "yes_b_c":
        await state.update_data(booking = 'Да')

        now = datetime.now(tz=pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        form_date = now.strftime("%H:%M %d.%m.%Y")
        await state.set_state(cl.RegPlayerStates.date_booking)
        await call.message.answer(f'Укажите время и дату в формате (<code>{form_date}</code>) 👇', parse_mode=ParseMode.HTML) 

    if call.data == "no_b_c":
        await state.update_data(booking = 'Нет')

        now = datetime.now(tz=pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        form_date = now.strftime("%H:%M %d.%m.%Y")
        await state.set_state(cl.RegPlayerStates.date_without_booking)
        await call.message.answer(f'Укажите время и дату, когда хотели бы поиграть в формате (<code>{form_date}</code>) 👇', parse_mode=ParseMode.HTML) 



@router.message(cl.RegPlayerStates.date_without_booking)
async def register_date(message: Message, state:FSMContext):
    await state.update_data(date_without_booking = message.text)
    await message.answer('Хотите оставить комментарий?', reply_markup=kb.comment_q)



@router.message(cl.RegPlayerStates.date_booking)
async def register_date(message: Message, state:FSMContext):
    await state.update_data(date_booking = message.text)
    await message.answer('Хотите оставить комментарий?', reply_markup=kb.comment_q)



@router.callback_query(F.data.in_(["yes_c", "no_c"]))
async def register_comment_q(call: CallbackQuery, state: FSMContext):
    await call.answer('')
    if call.data == "yes_c":
        await state.set_state(cl.RegPlayerStates.comment)
        await call.message.answer(f'Укажите комментарий 👇') 

    if call.data == "no_c":
        await register_card(None, call.message, state)



@router.message(cl.RegPlayerStates.comment)
async def register_comment(message: Message, state: FSMContext):
    await state.update_data(comment = message.text)
    await register_card(None, message, state)



async def register_card(callback: Optional[CallbackQuery], message: Message, state: FSMContext):
    data = await state.get_data()

    # Создаём объект PlayerData
    player_data = cl.PlayerData(
        id=data.get("user_id"),
        link=data.get("link"),
        age=data.get("age"),
        sex=data.get("sex"),
        date_booking=data.get("date_booking"),
        date_without_booking=data.get("date_without_booking"),
        comment=data.get("comment")
    )

    user_id = data.get("user_id")

    user = session.query(User).filter(User.tg_user_id == user_id).first()
    user_match = session.query(Match).filter((Match.id_tg_user == user_id) & ((Match.date_booking == data.get("date_booking")) | (Match.date_without_booking == data.get("date_booking")))).first()

    if user:
        if not user.age:
            user.age = data.get("age")
        if not user.sex:
            user.sex = data.get("sex")

    if user_match:
        user_match.date_booking = data.get("date_booking")
        user_match.date_without_booking = data.get("date_without_booking")
        user_match.comment = data.get("comment")
        print(f"Игра пользователя с ID {user_id} обновлена!")
    else:
        new_match = Match(id_tg_user = data.get("user_id"), date_booking = data.get("date_booking"), date_without_booking = data.get("date_without_booking"), comment = data.get("comment"))
        session.add(new_match)
        print(f"Карточка игры создана пользователем с ID {user_id}!")
    session.commit() # Сохраняем изменения (фиксируем транзакцию)

    await f.check_ban_user(user_id)

    if callback:
        await callback.message.answer('✅ Игра создана!')
        await callback.message.answer(f'<b>Ваша карточка игры выглядит так</b> 👇\n\n{player_data}', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.player)
    else:
        await message.answer('✅ Игра создана!')
        await message.answer(f'<b>Ваша карточка игры выглядит так</b> 👇\n\n{player_data}', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.player)


@router.callback_query(F.data == 'match_requests')
async def match_requests(callback: CallbackQuery):
    await callback.answer('')

    user_id = callback.from_user.id

    await f.check_ban_user(user_id)

    user = session.query(User).filter(User.tg_user_id == user_id).first()
    user_matches = session.query(Match).filter((Match.id_tg_user == user_id) & ((Match.player_1 == None) & (Match.player_2 == None))).all()

    if user_matches:
        if len(user_matches) == 1:
            await callback.message.answer(f'<b>Ваш запрос на игру выглядит так</b> 👇', parse_mode=ParseMode.HTML)
        else:
            await callback.message.answer(f'<b>Ваши запросы на игры выглядят так</b> 👇', parse_mode=ParseMode.HTML)

        for user_match in user_matches:
            if user and user_match:
                text = ''

                if user_match.date_booking:
                    text += f'\nБронь корта: {user_match.date_booking} 🎾'
                    
                if user_match.date_without_booking:
                    text += f'\nБрони нет! Предлагаю поиграть: {user_match.date_without_booking}'

                if user_match.comment:
                    text += f'\nКомментарий: <blockquote>{user_match.comment}</blockquote>'
                
                await callback.message.answer(f'<b>Запрос на игру</b> (ID: {user_match.match_id}) 🎾\n\n{user}{text}', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.player_get_card)
        if len(user_matches) < 3:
                await callback.message.answer(f'<b>Хотите создать ещё 1 запрос на игру?</b>', parse_mode=ParseMode.HTML, reply_markup=kb.add_card_q)

    else:
        await callback.message.answer("<b>Активных игр не найдено! Хотите создать?</b>", parse_mode=ParseMode.HTML, reply_markup=kb.create_card)



@router.callback_query(F.data == 'delete_match')
async def delete_match(callback: types.CallbackQuery, state: FSMContext):

    data = await state.get_data()
    user_id = data.get("user_id")
    
    message_text = callback.message.text or callback.message.caption  # Получаем текст сообщения
    match = re.search(r"ID: (\d+)", message_text)  # Ищем нужные значения

    if match:
        match_id = match.group(1)       # ID карточки
        
        user_match = session.query(Match).filter(Match.match_id == match_id).first()
        if user_match:
            session.delete(user_match)
            session.commit()

        await callback.answer(f"✅ Карточка удалена!", show_alert=False)
        print(f"✅ Карточка игры удалена пользователем с id {user_id}!")
    else:
        print("❌ При попытке удалить карточку игры произошла ошибка!")

    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()