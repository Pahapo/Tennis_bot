from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram import F, Router

import keywords.kw_tournament as kt
import handlers.btn_tournaments as bt
import handlers.create_tournament as ct

from config.db import session
from models.Tournament import Tournament


router = Router()


@router.callback_query(F.data == 'tournament_edit')
async def tournament_edit(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await callback.message.answer('<b>Тут вы можете отредактировать созданный турнир!</b>\nВыбери нужный турнир 👇', parse_mode=ParseMode.HTML, reply_markup=kt.tournament_info_edit)


@router.callback_query(F.data.in_(bt.get_list_tournaments_edit())) 
async def handle_level_buttons(call: CallbackQuery, state: FSMContext):
    await call.answer('')      

    selected_tournament = call.data.replace("_edit", "")  # Получаем название выбранного турнира
    tournament = session.query(Tournament).filter(Tournament.name_tournament == selected_tournament).first()
    await state.update_data(id_tournament = tournament.tournament_id)

    try:
        await ct.create_tournament(call, state)
    except Exception as e:
        print(f"Ошибка в create_tournament: {e}")