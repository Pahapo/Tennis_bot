import json
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

import handlers.keywords as kb
import handlers.classes as cl

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

    # Записываем словарь в список
    try:
        # Читаем существующие данные из файла
        with open("players_data.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл не существует, создаем пустой список
        users_data = []

    new_player_bool = True

    for i, user in enumerate(users_data):
        if str(user_id) in user:
            users_data[i] = player_data.get_data()  # Обновляем данные
            new_player_bool = False
            break
    
    if new_player_bool:
        users_data.append(player_data.get_data())

    with open("players_data.json", "w", encoding="utf-8") as file:
        json.dump(users_data, file, ensure_ascii=False, indent=4)

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

    try:
        # Читаем существующие данные из файла
        with open("players_data.json", "r", encoding="utf-8") as file:
            users_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл не существует, создаем пустой список
        users_data = []

    new_player_bool = True
    data_player_text = []

    for user in users_data:
        for key, data in user.items():
            if key == str(user_id):

                for key, value in data.items():
                    new_player_bool = False
                    
                    if key != 'Ссылка' and key != 'Уровень игры' and value != None:
                        data_player_text.append(f'{key}: {value}')

                user = '\n'.join(data_player_text)

                await callback.message.answer(f'<b>Ваша карточка выглядит так</b> 👇\n\n{user}\n\n⚠️ Обратите внимание, чтобы игрок смог связаться с вами и предложить игру, в настройках конфедециальности телеграм должен быть включен поиск по номеру\n• <b>Настройки -> Конфеденциальность -> Номер телефона -> <u>Все</u></b>', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.player)
                break

    # Проверяем, есть ли данные пользователя
    if new_player_bool:
        await callback.message.answer("<b>Карточка игрока ещё не создана!</b>\n\n• Создание карточки откроет доступ к поиску соперников", parse_mode=ParseMode.HTML, reply_markup=kb.create_card)
