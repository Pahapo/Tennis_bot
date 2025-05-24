from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.enums import ParseMode
from aiogram import F, Router
from config.config import EDITOR, ADMINS

import keywords.kw_any as kb
import keywords.kw_tournament as kt
import handlers.btn_tournaments as bt
import handlers.functions as f
import handlers.classes as cl
import handlers.start as st
import googleSheet.googleSheet as gs

from config.db import session
from models.TournamentPlayers import TournamentPlayers
from models.Tournament import Tournament
from models.Division import Division
from models.User import User


router = Router()


@router.callback_query(F.data == 'delete_players')
async def delete_players(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    tournament_info_del_players = bt.create_tournaments_keyboard_players(bt.get_list_tournaments_players())

    await callback.message.answer('<b>Тут вы можете удалить участника из турнира за нарушение или по веским причинам</b>\nВыбери нужный турнир 👇', parse_mode=ParseMode.HTML, reply_markup=tournament_info_del_players)


@router.callback_query(F.data.startswith("delete_player_"))
async def handle_level_buttons(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')      

    selected_players = callback.data.replace("delete_player_", "").replace("_players", "")  # Получаем название выбранного турнира
    await state.update_data(name_tournament_del_players = selected_players)

    await state.set_state(cl.FindUser.players_delete)
    await callback.message.answer('Введите <b>username</b> игрока 👇', parse_mode=ParseMode.HTML)
    

@router.message(cl.FindUser.players_delete)
async def find_name_del_players(message: Message, state:FSMContext):
    await state.update_data(players_delete = message.text)
    name_finder_user = message.text

    if '@' in name_finder_user:
        name_finder_user = name_finder_user.replace('@', '', 1)

    name_finder_user = 'https://t.me/' + name_finder_user

    options = LinkPreviewOptions(
        is_disabled=True
    )

    list_finder_user = [row[0] for row in session.query(User.link).all()]

    if name_finder_user in list_finder_user:
        user = session.query(User).filter(User.link == name_finder_user).first()

        data = await state.get_data()
        name_finder_tournament = data.get("name_tournament_del_players")
        await state.update_data(name_finder_user = name_finder_user)

        selected_tournament = session.query(Tournament).filter(Tournament.name_tournament == name_finder_tournament).first()
        find_user = session.query(TournamentPlayers).filter((TournamentPlayers.id_tg_user == user.tg_user_id) & (TournamentPlayers.id_tournament == selected_tournament.tournament_id)).first()
        
        if find_user == []:
            await message.answer(f'Пользователь <b>{user.name_user}</b> в {name_finder_tournament} не найден!',parse_mode=ParseMode.HTML, reply_markup=kb.back_delete_players)
        else:
            await state.update_data(tg_user_id = user.tg_user_id)
            await message.answer(f'<b>Найден пользователь {user.name_user} 🙋‍♂️</b>\n\nСсылка: {user.link}\nТурнир: {name_finder_tournament}', parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.edit_delete_players)
    else:
        await message.answer('Пользователь с таким <b>username</b> не найден!', parse_mode=ParseMode.HTML, reply_markup=kb.back_delete_players)

    
@router.callback_query(F.data == 'delete_players_tournaments')
async def delete_players_tournaments(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    user_id = callback.from_user.id
    if user_id in EDITOR or user_id in ADMINS:

        data = await state.get_data()
        name_finder_tournament = data.get("name_tournament_del_players")
        name_finder_user = data.get("name_finder_user")

        user = session.query(User).filter(User.link == name_finder_user).first()
        selected_division = session.query(Division).filter(Division.division_id == user.division_level).first()
        selected_tournament = session.query(Tournament).filter(Tournament.name_tournament == name_finder_tournament).first()
        
        # Удаление игрока из турнира
        session.query(TournamentPlayers).filter((TournamentPlayers.id_tg_user == user.tg_user_id) & (TournamentPlayers.id_tournament == selected_tournament.tournament_id)).delete()
        session.commit() # Сохраняем изменения (фиксируем транзакцию)

        try:
            gs.delete_player_from_tournament(name_finder_tournament, name_finder_user, selected_division.name_division)
            print(f"✅ Игрок удалён из Excel из турнира - '{selected_tournament.name_tournament}' дивизиона '{selected_division.name_division}'!")
            
            await callback.message.answer(f"✅ Пользователь {user.name_user} был исключён из турнира {name_finder_tournament}!", reply_markup=kb.exit)

            editors_list = await f.output_edits_list()
            message_text_send = f"<b>Дорогой {user.name_user}, мы вынуждены сообщить, что Вы были исключены из турнира {name_finder_tournament}</b> ❌\n\n<i>• Если это ошибка, пожалуйста, свяжитесь с редактором(-ами) турнира!</i> {editors_list}"

            options = LinkPreviewOptions(
                is_disabled=True
            )

            try:
                await bot.send_message(chat_id=user.tg_user_id, text=message_text_send, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.exit)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю с id: {user.tg_user_id} из-за ошибки: {e}")

        except Exception as e:
            print(f"Редактору не получилось удалить пользователя с id {user.tg_user_id} из турнира '{selected_tournament.name_tournament}' в дивизионе '{selected_division.name_division} 'из-за ошибки: {e}")
            await callback.message.answer(f"<b>Не получилось удалить пользователя {user.name_user} из турнира '{selected_tournament.name_tournament}' в дивизионе '{selected_division.name_division} 'из-за ошибки!</b>\n\nОбратитесь в поддержку 🙋‍♂️ @mm_sup", parse_mode=ParseMode.HTML, reply_markup=kb.exit)
        
        await state.clear()
    else:
        await callback.message.answer('Функция недоступна! Вы не организатор! ❌')
        st.cmd_start()







    






