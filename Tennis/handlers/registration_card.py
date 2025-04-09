import json
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

import handlers.keywords as kb
import handlers.classes as cl

from db import session
from models.User import User
from models.Contestant import Contestant

router = Router()

user_data = {}  # Ключ: username, значение: PlayerData


# РЕГИСТРАЦИЯ ИГРОКА

@router.callback_query(F.data == 'register_player')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    await state.set_state(cl.RegPlayerStates.name)
    await callback.message.answer('Введите ваше имя 👇')

@router.message(cl.RegPlayerStates.name)
async def register_name(message: Message, state:FSMContext):
    user_id = message.from_user.id
    user = message.from_user

    if user.username:
        user_link = f"https://t.me/{user.username}"
    else:
        user_link = f"tg://user?id={user.id}"
        
    await state.update_data(link = user_link)
    await state.update_data(id = user_id)
    # await state.update_data(skills = "")

    await state.update_data(name = message.text)
    await state.set_state(cl.RegPlayerStates.age)
    await message.answer('Введите ваш возраст 👇')

@router.message(cl.RegPlayerStates.age)
async def register_age(message: Message, state:FSMContext):
    await state.update_data(age = message.text)
    await message.answer('Выберите ваш пол 👇', reply_markup=kb.sex)

@router.callback_query(F.data.in_(["men", "women"]))
async def register_sex(call: CallbackQuery, state: FSMContext):
    await call.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    if call.data == "men":
        await state.update_data(sex = 'Мужчина')
    if call.data == "women":
        await state.update_data(sex = 'Женщина')
    await state.set_state(cl.RegPlayerStates.time)
    await call.message.answer('Введите предпочтительное время игры 👇')           

# @router.message(cl.RegPlayerStates.skills)
# async def register_age(message: Message, state:FSMContext):
#     await state.update_data(skills = message.text)
#     await state.set_state(cl.RegPlayerStates.time)
#     await message.answer('Введите предпочтительное время игры 👇')

@router.message(cl.RegPlayerStates.time)
async def register_time(message: Message, state: FSMContext):
    await state.update_data(time = message.text)
    
    data = await state.get_data()

    # Создаём объект PlayerData
    player_data = cl.PlayerData(
        id=data.get("id"),
        name=data.get("name"),
        link=data.get("link"),
        age=data.get("age"),
        sex=data.get("sex"),
        skills=data.get("skills"),
        time=data.get("time")
    )

    # Сохраняем данные в словарь
    user_id = message.from_user.id

    user = session.query(User).filter_by(tg_user_id = user_id).first()
    user_free_time = session.query(Contestant).filter_by(id_tg_user = user_id).first()
    if user:
        user.name_user = data.get("name")
        user.age = data.get("age")
        user.sex = data.get("sex")
        user_free_time.free_time_for_play = data.get("time")
        session.commit()
        print(f"Данные пользователя с ID {user_id} обновлены!")
    else:
        print(f"Пользователь {data.get("id")} отсутствует в базе.")

        new_user = User(tg_user_id = data.get("id"), name_user = data.get("name"), link = data.get("link"), age=data.get("age"), sex = data.get("sex"))
        session.add(new_user)  # Добавляем объект в сессию
        new_contestant = Contestant(free_time_for_play = data.get("time"), id_tg_user = data.get("id"))
        session.add(new_contestant)
        session.commit() # Сохраняем изменения (фиксируем транзакцию)

    await message.answer('✅ Карточка создана!')
    await message.answer(f'<b>Ваша карточка выглядит так</b> 👇\n\n{player_data}\n\n⚠️ Обратите внимание, чтобы игрок смог связаться с вами и предложить игру, в настройках конфедециальности телеграм должен быть включен поиск по номеру\n• <b>Настройки -> Конфеденциальность -> Номер телефона -> <u>Все</u></b>', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.player)
    await state.clear()



    
@router.callback_query(F.data == 'no_create_user_card')
async def no_create_user_card(callback: CallbackQuery):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    await callback.message.answer(f'<b>Карточка игрока ещё не создана!</b>\n\n• Создание карточки откроет доступ к поиску соперников', parse_mode=ParseMode.HTML, reply_markup=kb.create_card)



# Находит данные пользователя по username
# Когда нужно найти данные пользователя, просто обращайся к словарю по ключу (username).
@router.callback_query(F.data == 'get_data_player')
async def get_data_player(callback: CallbackQuery):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать

    user_id = callback.from_user.id

    user = session.query(User).filter_by(tg_user_id = user_id).first()
    user_free_time = session.query(Contestant).filter_by(id_tg_user = user_id).first()
    if user:
        print(f"Пользователь найден: ID={user.tg_user_id}, Name={user.name_user}")
        await callback.message.answer(f'<b>Ваша карточка выглядит так</b> 👇\n\n{user}Предпочтительное время игры: {user_free_time.free_time_for_play}\n\n⚠️ Обратите внимание, чтобы игрок смог связаться с вами и предложить игру, в настройках конфедециальности телеграм должен быть включен поиск по номеру\n• <b>Настройки -> Конфеденциальность -> Номер телефона -> <u>Все</u></b>', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.player)
    else:
        print("Пользователь не найден.")
        await callback.message.answer("<b>Карточка игрока ещё не создана!</b>\n\n• Создание карточки откроет доступ к поиску соперников", parse_mode=ParseMode.HTML, reply_markup=kb.create_card)