from aiogram import F, Router
from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram.enums import ParseMode
from config.config import ADMINS, MAIN_EDITOR, EDITOR

import keywords.kw_tournament as kb
import handlers.functions as f
import handlers.start as st

from config.db import session
from models.User import User
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers

router = Router()

message_text_send = ''

@router.callback_query(F.data == 'tournament_lists')
async def search_contestant(callback: CallbackQuery):
    await callback.answer('')

    user_id = callback.from_user.id
    if user_id in ADMINS or user_id in MAIN_EDITOR or user_id in EDITOR:
        
        tournaments = session.query(Tournament).all()
        if tournaments:
            await callback.message.answer(f"Список доступных турниров 👇", parse_mode=ParseMode.HTML)
        
            options = LinkPreviewOptions(
                is_disabled=True
            )

            list_tournaments = ''

            for tournament in tournaments:
                # Получаем имена и ссылки users, которые зарегистрировались на турнир
                users_in_tournament_without_name = session.query(TournamentPlayers).filter(TournamentPlayers.id_tournament == tournament.tournament_id).all()
                user_ids = [player.id_tg_user for player in users_in_tournament_without_name]  # Получаем список ID игроков
                users_in_tournament = session.query(User).filter(User.tg_user_id.in_(user_ids)).all()

                list_players = ''
                count_users_tournament = 0

                if int(tournament.division) == 1:
                    tournament_lvl = 'Золотой 🥇'
                elif int(tournament.division) == 2:
                    tournament_lvl = 'Серебряный 🥈'
                elif int(tournament.division) == 3:
                    tournament_lvl = 'Бронзовый 🥉'
                elif int(tournament.division) == 4:
                    tournament_lvl = 'Медный 🎾'
                elif int(tournament.division) == 5:
                    tournament_lvl = 'Железный 🏃‍♂️'
                else:
                    tournament_lvl = 'Все дивизионы'

                for user_in_tournament in users_in_tournament:
                    count_users_tournament += 1
                    list_players += f"{count_users_tournament}. <a href='{user_in_tournament.link}'>{user_in_tournament.name_user}</a>\n"

                list_tournaments += f"\n\n🏆 <b>Турнир {tournament.name_tournament.upper()}</b>\n\nАдрес корта: {tournament.address}\nДивизион турнира: {tournament_lvl}\nМаксимальное кол-во участников: {tournament.quantity_person} чел.\nНачало: {tournament.start_tournament}\nОкончание: {tournament.end_tournament}\nСтоимость участия: {tournament.price} бел.руб.\n\n🙋‍♂️ <b>Список участников ({count_users_tournament} чел.):</b>\n\n{list_players}"
                
            await callback.message.answer(list_tournaments, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.tournaments_data)
        else:
            await callback.message.answer(f"Нам жаль, но список 📂 турниров пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.tournaments_data)
    else:
        await callback.message.answer('Функция недоступна! Вы не являетесь организатором! 🚫')
        st.cmd_start()
    


