import os
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram import F, Router

import handlers.btn_tournaments as bt
import handlers.classes as cl

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
    await state.update_data(name = tournament.name_tournament)
    await state.update_data(type = tournament.type)
    await state.update_data(level = tournament.division)

    await state.set_state(cl.RegTournamentsStates.count)
    await callback.message.answer('Введите количество участников в каждом дивизионе 👇')

    # if os.path.exists(f"Tennis/img/tournament/{tournament.tournament_id}.jpg"):
    #     pyth_photo = f"Tennis/img/tournament/{tournament.tournament_id}.jpg"
    
    # try:        
    #     # Удаляем фото после успешной отправки
    #     os.remove(pyth_photo)
    # except Exception as e:
    #     print(f"Ошибка при удалении турнирного фото. Ошибка: {e}")

    # await state.set_state(cl.RegTournamentsStates.img_flag) # если пользователь отправит фото вне этого состояния, оно не будет обработано
    # await callback.message.answer('Отправьте фото турнира в формте .jpg 👇')