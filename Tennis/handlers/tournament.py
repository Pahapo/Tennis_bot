from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram.enums import ParseMode
from aiogram import F, Router
from sqlalchemy import func

import keywords.kw_start as ks
import keywords.kw_tournament as kb
import handlers.btn_tournaments as bt
import handlers.functions as f

from config.db import session
from models.TournamentPlayers import TournamentPlayers
from models.Tournament import Tournament
from models.Division import Division
from models.User import User


router = Router()


@router.callback_query(F.data == 'edit_tournament')
async def edit_tournament(callback: CallbackQuery):
    await callback.answer('')  # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    await callback.message.answer(f"<b>Тут происходит работа над турнирами начиная с их создания</b>\n\n• Создание турнира\n• Просмотр турниров\n• Просмотр/удаление участников\n• Редактировние турнира\n• Удаление турнира\n\nВыбери нужное 👇", parse_mode=ParseMode.HTML, reply_markup=ks.edit_tournament)
    

@router.callback_query(F.data == 'main_edit_tournament')
async def tournament_main_edit(callback: CallbackQuery):
    await callback.answer('')  # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать

    options = LinkPreviewOptions(
        is_disabled=True
    )

    editors_list = await f.output_edits_list()
    await callback.message.answer(f"<b>Тут происходит просмотр турниров и участников</b>\n\n• Если необходимо внести какие-либо изменения в турнир, свяжитесь с редактором(-ами) {editors_list}\n\nВыбери нужное 👇", parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=ks.main_edit_tournament)
    

@router.callback_query(F.data == 'tournament_info')
async def tournament_info(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await f.check_ban_user(callback.from_user.id) # проверка на бан

    if bt.get_list_tournaments() == []:
        await callback.message.answer(f'<b>Пусто</b> 🥲\n\nНам жаль, но в данный момент нет ни одного доступного турнира...', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    else: 
        await callback.message.answer(f"<b>Тут отображаются доступные турниры, в которых можно принять участие</b>\n\nДоступные турниры 👇", parse_mode=ParseMode.HTML, reply_markup=kb.tournament_info)
    

@router.callback_query(F.data.in_(bt.get_list_tournaments())) 
async def handle_level_buttons(call: CallbackQuery, state: FSMContext, bot):
    await call.answer('')      

    user_id = call.from_user.id
    selected_tournament = call.data  # Получаем название выбранного турнира
    await state.update_data(selected_tournament = selected_tournament)  # Сохраняем выбранный турнир в состояние

    # Получаем турнир
    tournament_data = session.query(Tournament).filter(Tournament.name_tournament == selected_tournament).first()
    # Запрос "зареган ли юзер на выбранный им турнир?"
    user_in_tournament = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == user_id, TournamentPlayers.id_tournament == tournament_data.tournament_id).all()
    # Запрос для подсчёта количества игроков
    player_count = session.query(func.count()).filter(TournamentPlayers.id_tournament == tournament_data.tournament_id).scalar()

    user = session.query(User).filter_by(tg_user_id = user_id).first()

    levelTournament_list = list(map(int, tournament_data.division.split(",")))
    name_division = session.query(Division).all()
    # Создаём словарь {division_id: name}, чтобы быстрее искать названия
    division_dict = {div.division_id: div.name_division for div in name_division}
    # Преобразуем список ID в список названий
    levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]

    tournament_lvl = ", ".join(levelTournament_names)

    if int(player_count) >= int(tournament_data.quantity_person):            
        await call.message.answer(f'<b>Мест больше нет</b> 🥲\n\nНам жаль, но на турнир уже записаться нельзя...\nПроверь другие доступные турниры или дождись нового 😎', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    elif user_in_tournament:
        await call.message.answer(f'<b>Вы уже участвуете в турнире!</b> ✅\n\nОжидайте завершения регистрации других участников', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    elif user.ban_status == True:
        await call.message.answer(f'<b>🚫 Вы не можете участвовать в турнире из-за бана</b>\n\nНам жаль, но на этот турнир записаться нельзя...\nБан будет снят {user.end_date_ban} 😎', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    elif user.division_level not in levelTournament_list:
        await call.message.answer(f'<b>⚠️ Вы не можете участвовать в турнире</b>\n\nК сожалению, этот турнир доступен только для дивизиона(-ов):\n{tournament_lvl}', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    elif user.division_level in levelTournament_list:
        await call.message.answer(f"{tournament_data.regulations}\n\n<b>ДЕТАЛИ ТУРНИРА</b> 🏆\n\n<b><i>Турнир \"{tournament_data.name_tournament.upper()}\"</i></b>\n📍 Адрес корта: {tournament_data.address}\n💪 Дивизион: {tournament_lvl}\n🙋‍♂️ Количество участников: {tournament_data.quantity_person} чел.\n📆 Начало: {tournament_data.start_tournament}\n📆 Окончание: {tournament_data.end_tournament}\n💰 Стоимость участия: {tournament_data.price} бел.руб.", parse_mode=ParseMode.HTML, reply_markup=kb.reglament)
    else:
        await call.message.answer(f"📋 <b>Какая-то ошибка</b>\n\nПожалуйста, если вы видите это сообщение, свяжитесь с нами 🙋‍♂️ @sup_MM", parse_mode=ParseMode.HTML, reply_markup=kb.exit)