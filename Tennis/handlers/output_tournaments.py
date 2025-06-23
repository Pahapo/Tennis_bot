from datetime import datetime, timedelta
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram.enums import ParseMode
from config.config import ADMINS, MAIN_EDITOR, EDITOR

import keywords.kw_tournament as kb
import handlers.functions as f

from config.db import session
from models.User import User
from models.Division import Division
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers

router = Router()

message_text_send = ''

@router.callback_query(F.data == 'tournament_lists')
async def search_match(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    user_id = callback.from_user.id
    if user_id in ADMINS or user_id in MAIN_EDITOR or user_id in EDITOR:
        
        tournaments = session.query(Tournament).all()
        if tournaments:
        
            options = LinkPreviewOptions(
                is_disabled=True
            )

            list_tournaments = ''

            for tournament in tournaments:
                # Получаем имена и ссылки users, которые зарегистрировались на турнир
                users_in_tournament_without_name = session.query(TournamentPlayers).filter(TournamentPlayers.id_tournament == tournament.tournament_id).all()
                user_ids = [player.id_tg_user for player in users_in_tournament_without_name]  # Получаем список ID игроков
                users_in_tournament = session.query(User).filter(User.tg_user_id.in_(user_ids)).all()

                levelTournament_list = list(map(int, tournament.division.split(",")))
                name_division = session.query(Division).all()
                # Создаём словарь {division_id: name}, чтобы быстрее искать названия
                division_dict = {div.division_id: div.name_division for div in name_division}
                # Преобразуем список ID в список названий
                levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]
                
                count_users_div = [0, 0, 0, 0, 0]
                list_players_div = ["", "", "", "", ""]

                for user_in_tournament in users_in_tournament:
                    if user_in_tournament.division_level == 1:
                        count_users_div[0] += 1
                        user_name_tg = user_in_tournament.link.replace("https://t.me/", "@")
                        list_players_div[0] += f"{count_users_div[0]}. <a href='{user_in_tournament.link}'>{user_in_tournament.name_user}</a> (<code>{user_name_tg}</code>)\n"
                    elif user_in_tournament.division_level == 2:
                        count_users_div[1] += 1
                        user_name_tg = user_in_tournament.link.replace("https://t.me/", "@")
                        list_players_div[1] += f"{count_users_div[1]}. <a href='{user_in_tournament.link}'>{user_in_tournament.name_user}</a> (<code>{user_name_tg}</code>)\n"
                    elif user_in_tournament.division_level == 3:
                        count_users_div[2] += 1
                        user_name_tg = user_in_tournament.link.replace("https://t.me/", "@")
                        list_players_div[2] += f"{count_users_div[2]}. <a href='{user_in_tournament.link}'>{user_in_tournament.name_user}</a> (<code>{user_name_tg}</code>)\n"
                    elif user_in_tournament.division_level == 4:
                        count_users_div[3] += 1
                        user_name_tg = user_in_tournament.link.replace("https://t.me/", "@")
                        list_players_div[3] += f"{count_users_div[3]}. <a href='{user_in_tournament.link}'>{user_in_tournament.name_user}</a> (<code>{user_name_tg}</code>)\n"
                    elif user_in_tournament.division_level == 5:
                        count_users_div[4] += 1
                        user_name_tg = user_in_tournament.link.replace("https://t.me/", "@")
                        list_players_div[4] += f"{count_users_div[4]}. <a href='{user_in_tournament.link}'>{user_in_tournament.name_user}</a> (<code>{user_name_tg}</code>)\n"
                
                list_players = ''
                for i in range(4):
                    if count_users_div[i] == 0:
                        continue
                    else:
                        list_players += f'<b>Дивизион: "{name_division[i].name_division}" ({count_users_div[i]} чел.)</b>\n{list_players_div[i]}\n\n'
                
                tournament_lvl = ", ".join(levelTournament_names)

                # проверка на актуальность турнира по времени
                end_date = datetime.today() - timedelta(days = 3)
                end_tournament = datetime.strptime(tournament.end_tournament, "%d.%m.%Y")
                if end_tournament >= end_date:
                    list_tournaments += f"\n\n🏆 <b>Турнир {tournament.name_tournament.upper()}</b>\n\nДивизион(-ы) турнира: {tournament_lvl}\nМаксимальное кол-во участников: {tournament.quantity_person} чел.\nНачало: {tournament.start_tournament}\nОкончание: {tournament.end_tournament}\nСтоимость участия: {tournament.price} бел.руб.\n\n🙋‍♂️ <b>СПИСОК УЧАСТНИКОВ:</b>\n\n{list_players}"
            
            if list_tournaments:
                await callback.message.answer(f"Список доступных турниров 👇", parse_mode=ParseMode.HTML)
                if user_id in ADMINS or user_id in MAIN_EDITOR:
                    await callback.message.answer(list_tournaments, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.tournaments_data)
                if user_id in EDITOR:
                    await callback.message.answer(list_tournaments, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.tournaments_data_edit)
            else:
                await callback.message.answer(f"Нам жаль, но список 📂 турниров пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.tournaments_data_exit)
        else:
            await callback.message.answer(f"Нам жаль, но список 📂 турниров пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.tournaments_data_exit)
    else:
        await callback.message.answer('Функция недоступна! Вы не являетесь организатором! ❌')
        await f.start_message(callback, bot)
    


