from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram import F, Router, types

import keywords.kw_tournament as kb
import handlers.classes as cl

from config.db import session
from models.TournamentPlayers import TournamentPlayers
from models.Tournament import Tournament

router = Router()

@router.callback_query(F.data == 'reglament_confirm')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await state.set_state(cl.RegTournamentPlayerStates.level)
    await callback.message.answer('Выберите ваш уровень игры 👇', parse_mode=ParseMode.HTML, reply_markup=kb.reg_tournament_lvl)


@router.callback_query(F.data.in_(["lvl_p_1", "lvl_p_2", "lvl_p_3", "lvl_p_4", "lvl_p_5", "lvl_p_6"]))
async def handle_level_buttons(call: CallbackQuery, state: FSMContext):
    await call.answer('')

    if call.data == "lvl_p_1":
        await state.update_data(level = 1)
    elif call.data == "lvl_p_2":
        await state.update_data(level = 2)
    elif call.data == "lvl_p_3":
        await state.update_data(level = 3)
    elif call.data == "lvl_p_4":
        await state.update_data(level = 4)
    elif call.data == "lvl_p_5":
        await state.update_data(level = 5)

    await call.message.answer('Комфортно ли играть групповой этап в будние дни в диапазоне с 18:00 до 21:00? 👇', parse_mode=ParseMode.HTML, reply_markup=kb.reg_tournament_time1)


@router.callback_query(F.data.in_(["time1_yes", "time1_no"]))
async def handle_time1_buttons(call: types.CallbackQuery, state:FSMContext): 
    await call.answer('')

    if call.data == "time1_yes":
        await state.update_data(time1 = True)
    elif call.data == "time1_no":
        await state.update_data(time1 = False)

    await call.message.answer('Комфортно ли играть плей-офф в выходные дни в диапазоне с 10:00 до 13:00? 👇', parse_mode=ParseMode.HTML, reply_markup=kb.reg_tournament_time2)


@router.callback_query(F.data.in_(["time2_yes", "time2_no"]))
async def handle_time2_buttons(call: types.CallbackQuery, state:FSMContext): 
    await call.answer('')

    if call.data == "time2_yes":
        await state.update_data(time2 = True)
    elif call.data == "time2_no":
        await state.update_data(time2 = False)

    data = await state.get_data()

    # Поиск id выбранного турнира
    selected_tournament = session.query(Tournament).filter(Tournament.name_tournament==data.get("selected_tournament")).first()
    # Запрос "зареган ли юзер на выбранный им турнир?"
    user_in_tournament = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == data.get("user_id"), TournamentPlayers.id_tournament == selected_tournament.tournament_id).all()

    if not user_in_tournament:
        user = TournamentPlayers(id_tournament = selected_tournament.tournament_id, id_tg_user = data.get("user_id"), time_workdays = data.get("time1"), time_weekends = data.get("time2"))
        session.add(user)
        session.commit()
        print(f"Игрок зарегистрировался на турнир - '{selected_tournament.name_tournament}'!")

    await call.message.answer('✅ <b>Регистрация завершена!</b>\n\nОжидайте завершения регистрации других участников', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    await state.clear()