from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.enums import ParseMode
from aiogram import F, Router
from config.config import EDITOR

import keywords.kw_any as kb
import keywords.kw_tournament as kt
import handlers.btn_tournaments as bt
import handlers.functions as f
import handlers.classes as cl
import handlers.start as st


from config.db import session
from models.TournamentPlayers import TournamentPlayers
from models.Tournament import Tournament
from models.User import User


router = Router()


@router.callback_query(F.data == 'delete_players')
async def delete_players(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await callback.message.answer('<b>Тут вы можете удалить участника из турнира за нарушение или по веским причинам</b>\nВыбери нужный турнир 👇', parse_mode=ParseMode.HTML, reply_markup=kt.tournament_info_del_players)



@router.callback_query(F.data.in_(bt.get_list_tournaments_players())) 
async def handle_level_buttons(call: CallbackQuery, state: FSMContext):
    await call.answer('')      

    selected_tournament = call.data.replace("_players", "")  # Получаем название выбранного турнира
    await state.update_data(name_tournament_del_players = selected_tournament)

    await state.set_state(cl.FindUser.players_delete)
    await call.message.answer('Введите <b>username</b> игрока 👇', parse_mode=ParseMode.HTML)
    

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

    
@router.callback_query(F.data == 'delete_players_tournaments')            # дописать автоматическое удаление из google таблицы пользователя
async def delete_players_tournaments(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    user_id = callback.from_user.id
    if user_id in EDITOR:

        data = await state.get_data()
        name_finder_tournament = data.get("name_tournament_del_players")
        name_finder_user = data.get("name_finder_user")

        user = session.query(User).filter(User.link == name_finder_user).first()
        selected_tournament = session.query(Tournament).filter(Tournament.name_tournament == name_finder_tournament).first()
        # Удаление игрока из турнира
        session.query(TournamentPlayers).filter((TournamentPlayers.id_tg_user == user.tg_user_id) & (TournamentPlayers.id_tournament == selected_tournament.tournament_id)).delete()
        session.commit() # Сохраняем изменения (фиксируем транзакцию)

        print(f"Пользователь '{user.name_user}' был исключён из турнира {name_finder_tournament}!")
        await callback.message.answer(f"✅ Пользователь '{user.name_user}' был исключён из турнира {name_finder_tournament}!", reply_markup=kb.back_delete_players)

        editors_list = await f.output_edits_list()
        message_text_send = f"<b>Дорогой {user.name_user}, мы вынуждены сообщить, что Вы были исключены из турнира {name_finder_tournament}</b> ❌\n\n<i>• Если это ошибка, пожалуйста, свяжитесь с редактором(-ами) турнира!</i> {editors_list}"

        options = LinkPreviewOptions(
            is_disabled=True
        )

        try:
            await bot.send_message(chat_id=user.tg_user_id, text=message_text_send, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.exit)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю с id: {user.tg_user_id} из-за ошибки: {e}")
        
        await state.clear()
    else:
        await callback.message.answer('Функция недоступна! Вы не организатор! ❌')
        st.cmd_start()







    






