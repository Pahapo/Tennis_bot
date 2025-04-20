from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from config.config import EDITOR

import keywords.kw_tournament as kb
import handlers.classes as cl
import handlers.start as st

from config.db import session
from models.Tournament import Tournament

import googleSheet.googleSheet as gs

router = Router()

user_data = {}  # Ключ: username, значение: PlayerData


# РЕГИСТРАЦИЯ ТУРНИРА

@router.callback_query(F.data == 'create_tournament')
async def create_tournament(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    user_id = callback.from_user.id
    await state.update_data(id_editor = user_id) # записали id редактора в состояние

    await state.set_state(cl.RegTournamentsStates.name)
    await callback.message.answer('Введите название турнира 👇')


@router.message(cl.RegTournamentsStates.name)
async def register_name(message: Message, state:FSMContext):

    await state.update_data(name = message.text)

    tournament = session.query(Tournament).filter(Tournament.name_tournament == message.text).first()
    if tournament:
        await state.set_state(cl.RegTournamentsStates.name)
        await message.answer('Турнир с таким именем уже существует! Придумайте другое имя 👇')
    else:
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
    await call.message.answer('Выберите дивизион турнира 👇', reply_markup=kb.level_tournament)


@router.callback_query(F.data.in_(["lvl_t_1", "lvl_t_2", "lvl_t_3", "lvl_t_4", "lvl_t_5", "lvl_t_all"]))
async def handle_level_buttons(call: CallbackQuery, state: FSMContext):
    await call.answer('')

    level = ''
    count_level = 0
    
    data = await state.get_data()
    if data.get("count_level") != None:
        count_level = data.get("count_level")

    if data.get("level") == None:

        if call.data == "lvl_t_1":
            level = '1'
        elif call.data == "lvl_t_2":
            level = '2'
        elif call.data == "lvl_t_3":
            level = '3'
        elif call.data == "lvl_t_4":
            level = '4'
        elif call.data == "lvl_t_5":
            level = '5'
        elif call.data == "lvl_t_all":
            level = '1,2,3,4,5'

        await state.update_data(level = level)
    else:
        if call.data == "lvl_t_1":
            level = ',1'
        elif call.data == "lvl_t_2":
            level = ',2'
        elif call.data == "lvl_t_3":
            level = ',3'
        elif call.data == "lvl_t_4":
            level = ',4'
        elif call.data == "lvl_t_5":
            level = ',5'

        level = data.get("level") + level   
        await state.update_data(level = level)

    count_level += 1
    await state.update_data(count_level = count_level)
    if level == '1,2,3,4,5' or count_level == 5:
        await not_add_level_tournament(call, state)
    else:
        await call.message.answer('Хотите добавить ещё 1 дивизион?', parse_mode=ParseMode.HTML, reply_markup=kb.add_level_tournament)


@router.callback_query(F.data == 'add_level_tournament')
async def add_level_tournament(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await state.set_state(cl.RegTournamentsStates.level)
    await callback.message.answer('Выберите дивизион турнира 👇', reply_markup=kb.level_tournament)


@router.callback_query(F.data == 'not_add_level_tournament')
async def not_add_level_tournament(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await state.set_state(cl.RegTournamentsStates.count)
    await callback.message.answer('Введите максимальное количество участников 👇')


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
    
    if data.get("id_editor") in EDITOR:

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

    tournament = session.query(Tournament).filter(Tournament.tournament_id == data.get("id_tournament")).first()
    if tournament:
        tournament.name_tournament = data.get("name")
        tournament.address = data.get("address")
        tournament.division = data.get("level")
        tournament.quantity_person = int(data.get("count"))
        tournament.start_tournament = data.get("time1")
        tournament.end_tournament = data.get("time2")
        tournament.price = int(data.get("price"))
        session.commit()

        link_sheet_tournament = tournament.link_table

        print(f"Турнир - '{data.get("name")}' был обновлён редактором!")
        await message.answer('✅ Турнир обновлён!\n\n• Если вы изменили название турнира, оно не будет изменено в названии exel таблицы.\n\nИсправьте самостоятельно или обратитесь в поддержку\n🙋‍♂️ Поддержка @sup_MM')

    else:
        print(f"Создан новый турнир - '{data.get("name")}'.")
        await message.answer('⏰ Начинаем создавать турнир и excel таблицу...')

        link_sheet_tournament = gs.startDoingSheet(data.get("name"), data.get("level"))
        
        new_tournament = Tournament(name_tournament = data.get("name"), address = data.get("address"), division = data.get("level"), quantity_person = int(data.get("count")), start_tournament = data.get("time1"), end_tournament = data.get("time2"), price = int(data.get("price")), link_table = link_sheet_tournament)
        session.add(new_tournament)  # Добавляем объект в сессию
        session.commit() # Сохраняем изменения (фиксируем транзакцию)

        await message.answer('✅ Турнир создан!')

    await message.answer(f"<b>Турнирная карточка выглядит так</b> 👇\n\n{tournament_data}Ссылка на турнир: {link_sheet_tournament}\n\n• Ссылки на турниры находятся в разделе \"Турнирные таблицы 📋\"", parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.tournament)
    await state.clear()
