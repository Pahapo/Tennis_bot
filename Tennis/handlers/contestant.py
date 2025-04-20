from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import F, Router

import keywords.kw_user as kb
import handlers.functions as f

from config.db import session
from models.User import User
from models.Division import Division
from models.Contestant import Contestant
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers

router = Router()

message_text_send = ''


@router.callback_query(F.data == 'contestant')
async def contestant(callback: CallbackQuery, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        await callback.message.answer(f"<b>Тут ты можешь найти соперника</b> 🙋‍♂️ по уровню игры, возрасту и даже по истории сыгранных турниров\n\n• Создай свою карточку, чтобы другие игроки могли найти тебя 👇\n\n<i>Фильтрация станет доступна в новом обновлении бота</i>", parse_mode=ParseMode.HTML, reply_markup=kb.players)
    else:
        await f.check_subscription_message(callback)


@router.callback_query(F.data == 'search_contestant')
async def search_contestant(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')

    data = await state.get_data()
    user_id = data.get("user_id") # взяли из состояния, которое записалось при /start

    tg_users_id = [row[0] for row in session.query(Contestant.id_tg_user).all()]
    count_users = len(tg_users_id)
    if user_id in tg_users_id:
        count_users -= 1

    if count_users >= 1:
        await callback.message.answer(f"Список доступных соперников 👇", parse_mode=ParseMode.HTML)
    
        options = LinkPreviewOptions(
            is_disabled=True
        )

        users = session.query(User).all()  # Получаем список объектов User
        users_free_time = session.query(Contestant).filter(Contestant.free_time_for_play != None).all()  # Получаем список User с указанным free_time

        list_contestants = ''
       
        for user_free_time in users_free_time:
        
                for user in users:
                    if user.tg_user_id == user_id:
                        continue
                    elif user.tg_user_id == user_free_time.id_tg_user:
                        user_in_tournaments = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == user.tg_user_id).all()     # ИСПРАВИТЬ, ЧТОБЫ НЕ ОБРАЩАТЬСЯ К БД КАЖДЫЙ РАЗ
                        tournament_ids = [games.id_tournament for games in user_in_tournaments]  # Получаем список ID игроков
                        history_tournaments = session.query(Tournament).filter(Tournament.tournament_id.in_(tournament_ids)).all()         # ИСПРАВИТЬ, ЧТОБЫ НЕ ОБРАЩАТЬСЯ К БД КАЖДЫЙ РАЗ

                        history = ''
                        division_lvl = ''

                        for toutnament in history_tournaments:
                            if history == '':
                                history += f"\"{toutnament.name_tournament}\""
                            else:
                                history += f", \"{toutnament.name_tournament}\""

                        if history == '':
                            history = 'Не участвовал(-а) 🥲'

                        if user.division_level != None:
                            name_division = session.query(Division).filter(Division.division_id == int(user.division_level)).first()
                            division_lvl = name_division.name_division
                        else:
                            division_lvl = 'Не определён'

                        # Добавить вывод рейтинга в скобках возле имени
                        list_contestants += f'\n\n🙋‍♂️ <b>{user.name_user.upper()}</b>\n\nСсылка: <tg-spoiler>{user.link}</tg-spoiler>\nИстория турниров: {history}\nДивизион: {division_lvl}\nВозраст: {user.age}\nПол: {user.sex}\nПредпочтительное время игры: <blockquote>{user_free_time.free_time_for_play}</blockquote>'
            
        await callback.message.answer(list_contestants, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.players_data)
    else:
        await callback.message.answer(f"Нам жаль, но список 📂 доступных соперников пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.players_data)
    


