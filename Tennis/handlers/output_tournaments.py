from aiogram import F, Router
from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram.enums import ParseMode

import keywords.kw_tournament as kb
import handlers.functions as f

from config.db import session
from models.Tournament import Tournament

router = Router()

message_text_send = ''

@router.callback_query(F.data == 'tournament_lists')
async def search_contestant(callback: CallbackQuery):
    await callback.answer('')

    tournaments = session.query(Tournament).all()
    if tournaments:
        await callback.message.answer(f"Список доступных турниров 👇", parse_mode=ParseMode.HTML)
    
        options = LinkPreviewOptions(
            is_disabled=True
        )

        list_tournaments = ''

        for tournament in tournaments:
            list_tournaments += f'\n\n🏆 <b>Турнир {tournament.name_tournament.upper()}</b>\n\nАдрес корта: {tournament.address}\nУровень турнира: {tournament.division}\nМаксимальное кол-во участников: {tournament.quantity_person} чел.\nНачало: {tournament.start_tournament}\nОкончание: {tournament.end_tournament}\nСтоимость участия: {tournament.price} бел.руб.'
             
        await callback.message.answer(list_tournaments, parse_mode=ParseMode.HTML, link_preview_options=options, reply_markup=kb.tournaments_data)
    else:
        await callback.message.answer(f"Нам жаль, но список 📂 турниров пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.tournaments_data)
    


