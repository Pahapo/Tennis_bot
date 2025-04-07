import json
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram import F, Router, types

import handlers.keywords as kb
import handlers.classes as cl

router = Router()

# Если у пользователя есть БАН, то он видит другое сообщение
# Добавить проверку, и, если человек уже зарегистрирован на турнир, то написать ему об этом


@router.callback_query(F.data == 'reglament_confirm')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    await state.set_state(cl.RegTournamentPlayerStates.level)
    await callback.message.answer('Выберите ваш уровень игры 👇', parse_mode=ParseMode.HTML, reply_markup=kb.reg_tournament_lvl)


@router.callback_query(F.data.in_(["lvl_p_1", "lvl_p_2", "lvl_p_3", "lvl_p_4", "lvl_p_5", "lvl_p_6"]))
async def handle_level_buttons(call: CallbackQuery, state: FSMContext):
    await call.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать

    if call.data == "lvl_p_1":
        await state.update_data(level = "Золотой")
    elif call.data == "lvl_p_2":
        await state.update_data(level = "Серебряный")
    elif call.data == "lvl_p_3":
        await state.update_data(level = "Бронзовый")
    elif call.data == "lvl_p_4":
        await state.update_data(level = "Медный")
    elif call.data == "lvl_p_5":
        await state.update_data(level = "Железный")

    await call.message.answer('Комфортно ли играть групповой этап в будние дни в диапазоне с 18:00 до 21:00? 👇', parse_mode=ParseMode.HTML, reply_markup=kb.reg_tournament_time1)


@router.callback_query(F.data.in_(["time1_yes", "time1_no"]))
async def handle_time1_buttons(call: types.CallbackQuery, state:FSMContext): 
    await call.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать

    if call.data == "time1_yes":
        await state.update_data(time1 = True)
    elif call.data == "time1_no":
        await state.update_data(time1 = False)

    await call.message.answer('Комфортно ли играть плей-офф в выходные дни в диапазоне с 10:00 до 13:00? 👇', parse_mode=ParseMode.HTML, reply_markup=kb.reg_tournament_time2)



@router.callback_query(F.data.in_(["time2_yes", "time2_no"]))
async def handle_time2_buttons(call: types.CallbackQuery, state:FSMContext): 
    await call.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать

    if call.data == "time2_yes":
        await state.update_data(time2 = True)
    elif call.data == "time2_no":
        await state.update_data(time2 = False)

    data = await state.get_data()

    # Создаём объект PlayerData
    player_data = cl.TournamentPlayerData(
        id=data.get("user_id"), # взяли из состояния
        name=data.get("user_name"),
        link=data.get("user_link"),
        level=data.get("level"),
        time1=data.get("time1"),
        time2=data.get("time2")
    )

    # Сохраняем данные в словарь
    user_id = call.message.from_user.id

    # Записываем словарь в список
    try:
        # Читаем существующие данные из файла
        with open("Пекин.json", "r", encoding="utf-8") as file:     # ИСПРАВИТЬ ПОД БД
            tournament_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл не существует, создаем пустой список
        tournament_data = []

    new_player_bool = True

    for i, user in enumerate(tournament_data):
        if str(user_id) in user:
            tournament_data[i] = player_data.get_data()  # Обновляем данные
            new_player_bool = False
            break
    
    if new_player_bool:
        tournament_data.append(player_data.get_data())

    with open("Пекин.json", "w", encoding="utf-8") as file:                 # ИСПРАВИТЬ ПОД БД
        json.dump(tournament_data, file, ensure_ascii=False, indent=4)

    await call.message.answer('✅ <b>Регистрация завершена!</b>\n\nОжидайте завершения регистрации других участников', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    await state.clear()