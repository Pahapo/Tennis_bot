import json
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

import keywords.kw_tournament as kb
import handlers.classes as cl

from config.db import session
from models.Tournament import Tournament

import googleSheet.googleSheet as gs

router = Router()

user_data = {}  # Ключ: username, значение: PlayerData


# РЕГИСТРАЦИЯ ТУРНИРА

@router.callback_query(F.data == 'register_tournament')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await state.set_state(cl.RegTournamentsStates.name)
    await callback.message.answer('Введите название турнира 👇')

@router.message(cl.RegTournamentsStates.name)
async def register_name(message: Message, state:FSMContext):

    await state.update_data(name = message.text)
    await state.set_state(cl.RegTournamentsStates.address)
    await message.answer('Выберите адрес корта 👇', reply_markup=kb.address_court)

@router.callback_query(F.data.in_(["court_1", "court_2", "court_3", "court_4", "court_5"]))
async def handle_level_buttons(call: CallbackQuery, state: FSMContext):
    await call.answer('')
    
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
    await call.answer('')
    
    if call.data == "lvl_t_1":
        await state.update_data(level = 1)
    elif call.data == "lvl_t_2":
        await state.update_data(level = 2)
    elif call.data == "lvl_t_3":
        await state.update_data(level = 3)
    elif call.data == "lvl_t_4":
        await state.update_data(level = 4)
    elif call.data == "lvl_t_5":
        await state.update_data(level = 5)
    elif call.data == "lvl_t_all":
        await state.update_data(level = [1, 2, 3, 4, 5])
    
    await state.set_state(cl.RegTournamentsStates.count)
    await call.message.answer('Введите максимальное количество участников 👇')

@router.message(cl.RegTournamentsStates.count)
async def register_age(message: Message, state:FSMContext):
    
    await state.update_data(count = message.text)
    await state.set_state(cl.RegTournamentsStates.time1)
    await message.answer('Введите дату начала турнира\n\nФормат: 01.01.2025 👇')

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

    tournament = session.query(Tournament).filter_by(name_tournament = data.get("name")).first()
    if tournament:
        tournament.name_tournament = data.get("name")
        tournament.address = data.get("address")
        tournament.division = data.get("level")  # нельзя изменять дивизионы. Листы в гугл-таблице уже созданы. Или сделать удаление листов 
        tournament.quantity_person = int(data.get("count"))
        tournament.start_tournament = data.get("time1")
        tournament.end_tournament = data.get("time2")
        tournament.price = int(data.get("price"))
        session.commit()
        print(f"Турнир - '{data.get("name")}' был обновлён редактором!")
    else:
        print(f"Создан новый турнир - '{data.get("name")}'.")
        new_tournament = Tournament(name_tournament = data.get("name"), address = data.get("address"), division = data.get("level"), quantity_person = int(data.get("count")), start_tournament = data.get("time1"), end_tournament = data.get("time2"), price = int(data.get("price")))
        session.add(new_tournament)  # Добавляем объект в сессию
        session.commit() # Сохраняем изменения (фиксируем транзакцию


        # gs.startDoingSheet(data.get("name"), data.get("level"))  # --- ЗДЕСЬ! ---

    await message.answer('✅ Турнир создан!')
    await message.answer(f'<b>Турнирная карточка выглядит так</b> 👇\n\n{tournament_data}', parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.tournament)
    await state.clear()
