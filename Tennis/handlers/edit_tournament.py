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
    tournament_info_edit = bt.create_tournaments_edit_keyboard(bt.get_list_tournaments_edit())

    await callback.message.answer('<b>Тут вы можете отредактировать созданный турнир!</b>\nВыбери нужный турнир 👇', parse_mode=ParseMode.HTML, reply_markup=tournament_info_edit)

   
@router.callback_query(F.data.startswith("tournament_edit_"))
async def handle_level_buttons(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')       
    selected_tournament = callback.data.replace("tournament_edit_", "").replace("_edit", "")  # Получаем название выбранного турнира
    tournament = session.query(Tournament).filter(Tournament.name_tournament == selected_tournament).first()
    await state.update_data(id_tournament = tournament.tournament_id)

    try:
        await ct.create_tournament(callback, state)
    except Exception as e:
        print(f"Ошибка в create_tournament! Подробнее: {e}")