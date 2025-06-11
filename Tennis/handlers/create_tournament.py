import pytz
import asyncio
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
from sqlalchemy import inspect
from config.config import EDITOR

import handlers.classes as cl
import handlers.functions as f
import keywords.kw_tournament as kb
import handlers.validation as valid

from config.db import session
from models.Tournament import Tournament

import googleSheet.googleSheet as gs

router = Router()

user_data = {}  # Ключ: username, значение: PlayerData
MOSCOW_TZ = pytz.timezone('Europe/Moscow')


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

    # Инспектируем таблицу Tournament
    mapper = inspect(Tournament)    
    # Получаем размер `name_tournament`
    name_tournament_length = mapper.columns["name_tournament"].type.length

    if len(message.text) > name_tournament_length:
        await message.answer(f"⚠ Ошибка! Текст превышает {name_tournament_length} символов")
        return  # Останавливаем обработку, чтобы пользователь ввел данные снова

    await state.set_state(None)  
    await state.update_data(name = message.text)

    tournament = session.query(Tournament).filter(Tournament.name_tournament == message.text).first()
    if tournament:
        await state.set_state(cl.RegTournamentsStates.name)
        await message.answer('Турнир с таким именем уже существует! Придумайте другое имя 👇')
    else:  
        data = await state.get_data()
        tournament = session.query(Tournament).filter(Tournament.tournament_id == data.get("id_tournament")).first()
        if tournament:
            await state.set_state(cl.RegTournamentsStates.count)
            await message.answer('Введите количество участников в 1 дивизионе 👇')
            await state.update_data(level = tournament.division)
        else:
            await state.set_state(cl.RegTournamentsStates.level)
            await message.answer('Выберите дивизион турнира 👇', reply_markup=kb.level_tournament)


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

        if level[1] not in data.get("level"):
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
    await state.set_state(cl.RegTournamentsStates.type)
    await callback.message.answer('Выберите тип турнира 👇', reply_markup=kb.type_tournament)


@router.callback_query(F.data.in_(["type_t_1", "type_t_2", "type_t_3", "type_t_4", "type_t_5", "type_t_6"]))
async def handle_types_buttons(call: CallbackQuery, state: FSMContext):
    await call.answer('')

    if call.data == "type_t_1":
        type = 'Одиночный'
    if call.data == "type_t_2":
        type = 'Парный'
    if call.data == "type_t_3":
        type = 'Микст'
    if call.data == "type_t_4":
        type = 'Командный'
    if call.data == "type_t_5":
        type = 'Марафон'
    if call.data == "type_t_6":
        type = 'Тай-Брейк'

    await state.update_data(type = type)

    await state.set_state(cl.RegTournamentsStates.count)
    await call.message.answer('Введите количество участников в каждом дивизионе 👇')


@router.message(cl.RegTournamentsStates.count)
async def register_age(message: Message, state:FSMContext):

    # Проверяем, корректно ли введено количество участников
    if not valid.validate_isdigit(message.text):
        await message.answer("⚠ Ошибка! Введите <b>целое положительное число</b>", parse_mode=ParseMode.HTML)
        return  # Останавливаем обработку, чтобы пользователь ввел данные снова

    await state.update_data(count = message.text)
    await state.set_state(None)
    
    form_date = (datetime.now(tz=MOSCOW_TZ) + timedelta(days=7)).strftime('%d.%m.%Y')
    
    await state.set_state(cl.RegTournamentsStates.time1)
    await message.answer(f'Введите дату начала турнира 👇\n\nФормат: <code>{form_date}</code>', parse_mode=ParseMode.HTML)


@router.message(cl.RegTournamentsStates.time1)
async def register_age(message: Message, state:FSMContext):

    if not valid.validate_date(message.text):
        await message.answer("⚠ Ошибка! Формат даты должен быть <b>DD.MM.YYYY</b>, и дата в будущем времени. Попробуйте снова", parse_mode=ParseMode.HTML)
        return  # Останавливаем обработку
    
    await state.update_data(time1 = message.text)
    await state.set_state(None)
    
    form_date = (datetime.now(tz=MOSCOW_TZ) + timedelta(days=37)).strftime('%d.%m.%Y')

    await state.set_state(cl.RegTournamentsStates.time2)
    await message.answer(f'Введите дату окончания турнира 👇\n\nФормат: <code>{form_date}</code>', parse_mode=ParseMode.HTML)


@router.message(cl.RegTournamentsStates.time2)
async def register_age(message: Message, state:FSMContext):

    if not valid.validate_date(message.text):
        await message.answer("⚠ Ошибка! Формат даты должен быть <b>DD.MM.YYYY</b>, и дата в будущем времени. Попробуйте снова", parse_mode=ParseMode.HTML)
        return  # Останавливаем обработку
    
    await state.update_data(time2 = message.text)
    await state.set_state(None)
    
    await state.set_state(cl.RegTournamentsStates.price)
    await message.answer('Введите стоимость участия в турнире (только цифры) 👇')


@router.message(cl.RegTournamentsStates.price)
async def register_age(message: Message, state:FSMContext):

    if not valid.validate_isdigit(message.text):
        await message.answer("⚠ Ошибка! Введите <b>целое положительное число</b>", parse_mode=ParseMode.HTML)
        return  # Останавливаем обработку, чтобы пользователь ввел данные снова
    
    await state.update_data(price = message.text)
    await state.set_state(None)

    await state.set_state(cl.RegTournamentsStates.regulations)
    await message.answer('Введите текст регламента 👇')


@router.message(cl.RegTournamentsStates.regulations)
async def register_age(message: Message, state:FSMContext, bot):

    if len(message.text) > 2500:
        await message.answer(f"⚠ Ошибка! Текст превышает 2500 символов")
        return  # Останавливаем обработку, чтобы пользователь ввел данные снова

    await state.update_data(regulations = message.html_text)
    await state.set_state(None)
    
    data = await state.get_data()
    
    if data.get("id_editor") in EDITOR:

        # Создаём объект PlayerData
        tournament_data = cl.TournamentsData(
            name=data.get("name"),
            level=data.get("level"),
            type=data.get("type"),
            count=int(data.get("count")),
            time1=data.get("time1"),
            time2=data.get("time2"),
            price=int(data.get("price")),
            regulations=data.get("regulations")
        )

    tournament = session.query(Tournament).filter(Tournament.tournament_id == data.get("id_tournament")).first()
    if tournament:

        gs.edit_name_tournament(tournament.name_tournament, data.get("name"))
        
        old_name = tournament.name_tournament

        tournament.name_tournament = data.get("name")
        tournament.type = data.get("type")
        tournament.quantity_person = int(data.get("count"))
        tournament.start_tournament = data.get("time1")
        tournament.end_tournament = data.get("time2")
        tournament.price = int(data.get("price"))
        tournament.regulations = data.get("regulations")
        session.commit()

        link_sheet_tournament = tournament.link_table

        print(f'Турнир "{old_name}" был обновлён редактором на "{data.get("name")}"!')
        await message.answer('✅ Турнир обновлён!')

    else:
        tournament_sms = await message.answer('⏰ Начинаем создавать турнир')
        await asyncio.sleep(2)
        await tournament_sms.edit_text("Создаём Excel таблицу... 📁")
        
        type_tournament = f'Турнир {data.get("type")} (шаблон)'
        link_sheet_tournament = gs.startDoingSheet(data.get("name"), data.get("level"), int(data.get("count")), type_tournament)

        await tournament_sms.edit_text("Добавляем участников... 🙋‍♂️")
        
        new_tournament = Tournament(name_tournament = data.get("name"), division = data.get("level"), type = data.get("type"), quantity_person = int(data.get("count")), start_tournament = data.get("time1"), end_tournament = data.get("time2"), price = int(data.get("price")), link_table = link_sheet_tournament, regulations = data.get("regulations"))
        session.add(new_tournament)  # Добавляем объект в сессию
        session.commit() # Сохраняем изменения (фиксируем транзакцию)

        await tournament_sms.edit_text('✅ Турнир создан!')
        print(f'Создан новый турнир - "{data.get("name")}"')

        await f.notification_about_new_tournament(data.get("name"), data.get("time1"), data.get("level"), bot)
        
    try:
        await message.answer(f"<b>Турнирная карточка выглядит так</b> 👇\n\n{tournament_data}Ссылка на турнир: {link_sheet_tournament}\n\n• Ссылки на турниры находятся в разделе \"Турнирные таблицы 📋\"", parse_mode=ParseMode.HTML, disable_web_page_preview=True, reply_markup=kb.tournament)
    except Exception as e:
        print(f"Сообщение с турнирной карточкой не удалось вывести редактору из-за ошибки: {e}")
        await message.answer("<b>Турнирная карточка по какой-то причине не вывелась!</b>\n\nОбратитесь в поддержку 🙋‍♂️ @mm_sup", parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    await state.clear()

