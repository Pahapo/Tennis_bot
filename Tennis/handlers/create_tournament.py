import json
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

import handlers.keywords as kb
import handlers.classes as cl

router = Router()

user_data = {}  # Ключ: username, значение: PlayerData


# РЕГИСТРАЦИЯ ТУРНИРА

@router.callback_query(F.data == 'register_tournament')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    await state.set_state(cl.RegTournamentsStates.name)
    await callback.message.answer('Введите название турнира 👇')

@router.message(cl.RegTournamentsStates.name)
async def register_name(message: Message, state:FSMContext):

    await state.update_data(name = message.text)
    await state.set_state(cl.RegTournamentsStates.address)
    await message.answer('Выберите адрес корта 👇', reply_markup=kb.address_court)

@router.callback_query(F.data.in_(["court_1", "court_2", "court_3", "court_4", "court_5"]))
async def handle_level_buttons(call: CallbackQuery, state: FSMContext):
    await call.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    
    if call.data == "court_1":
        await state.update_data(address = "Северная Америка - Кижеватова 3Б")
    elif call.data == "court_2":
        await state.update_data(address = "Африка - Теслы 6")
    elif call.data == "court_3":
        await state.update_data(address = "Центральная Европа - Теслы 16")
    elif call.data == "court_4":
        await state.update_data(address = "Средиземноморский - Теслы 24")
    elif call.data == "court_5":
        await state.update_data(address = "Тропические острова - Лученка 24")

    await state.set_state(cl.RegTournamentsStates.level)
    await call.message.answer('Выберите уровень турнира 👇', reply_markup=kb.level_tournament)

@router.callback_query(F.data.in_(["lvl_t_1", "lvl_t_2", "lvl_t_3", "lvl_t_4", "lvl_t_5", "lvl_t_all"]))
async def handle_level_buttons(call: CallbackQuery, state: FSMContext):
    await call.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    
    if call.data == "lvl_t_1":
        await state.update_data(level = "Золотой")
    elif call.data == "lvl_t_2":
        await state.update_data(level = "Серебряный")
    elif call.data == "lvl_t_3":
        await state.update_data(level = "Бронзовый")
    elif call.data == "lvl_t_4":
        await state.update_data(level = "Медный")
    elif call.data == "lvl_t_5":
        await state.update_data(level = "Железный")
    elif call.data == "lvl_t_all":
        await state.update_data(level = ["Золотой", "Серебряный", "Бронзовый", "Медный", "Железный"])
    
    await state.set_state(cl.RegTournamentsStates.count)
    await call.message.answer('Введите максимальное количество участников 👇')

@router.message(cl.RegTournamentsStates.count)
async def register_age(message: Message, state:FSMContext):
    
    await state.update_data(count = message.text)
    await state.set_state(cl.RegTournamentsStates.time1)
    await message.answer('Введите дату окончания турнира\n\nФормат: 01.01.2025 👇')

@router.message(cl.RegTournamentsStates.time1)
async def register_age(message: Message, state:FSMContext):
    
    await state.update_data(time1 = message.text)
    await state.set_state(cl.RegTournamentsStates.time2)
    await message.answer('Введите дату окончания турнира\n\nФормат: 01.01.2025 👇')

@router.message(cl.RegTournamentsStates.time2)
async def register_age(message: Message, state:FSMContext):
    
    await state.update_data(time2 = message.text)
    await state.set_state(cl.RegTournamentsStates.price)
    await message.answer('Введите стоимость участия в турнире (только цифры) 👇')

@router.message(cl.RegTournamentsStates.price)
async def register_age(message: Message, state:FSMContext):
    
    await state.update_data(price = message.text)
    
    data = await state.get_data()

    # Создаём объект PlayerData
    tournament_data = cl.TournamentsData(
        name=data.get("name"),
        address=data.get("address"),
        level=data.get("level"),
        count=int(data.get("count")),
        time1=data.get("time1"),
        time2=data.get("time2"),
        price=int(data.get("price"))
    )

    # Сохраняем данные в словарь
    name_tournament = data.get("name")

    # Записываем словарь в список
    try:
        # Читаем существующие данные из файла
        with open("tournaments.json", "r", encoding="utf-8") as file:
            tournaments_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файл не существует, создаем пустой список
        tournaments_data = []

    new_tournament_bool = True

    for i, tournament in enumerate(tournaments_data):
        if name_tournament in tournament:
            tournaments_data[i] = tournament_data.get_data()  # Обновляем данные
            new_tournament_bool = False
            break
    
    if new_tournament_bool:
        tournaments_data.append(tournament_data.get_data())

    with open("tournaments.json", "w", encoding="utf-8") as file:
        json.dump(tournaments_data, file, ensure_ascii=False, indent=4)

    await message.answer('✅ Турнир создан!')
    await message.answer(f'<b>Турнирная карточка выглядит так</b> 👇\n\n{tournament_data}', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.tournament)
    await state.clear()
