import os
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LinkPreviewOptions, FSInputFile
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram import F, Router
from sqlalchemy import func
from config.config import ADMINS, MAIN_EDITOR, EDITOR

import keywords.kw_start as ks
import keywords.kw_tournament as kb
import handlers.btn_tournaments as bt
import handlers.functions as f

from config.db_utils import get_db_readonly, get_db
from sqlalchemy import select
from models.TournamentPlayers import TournamentPlayers
from models.Tournament import Tournament
from models.Division import Division
from models.User import User


router = Router()


@router.callback_query(F.data == 'edit_tournament')
async def edit_tournament(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(f"<b>Тут происходит работа над турнирами начиная с их создания</b>\n\n• Создание турнира\n• Просмотр турниров\n• Просмотр/удаление участников\n• Редактирование турнира\n• Удаление турнира\n\nВыбери нужное 👇", parse_mode=ParseMode.HTML, reply_markup=ks.edit_tournament)
    

@router.callback_query(F.data == 'main_edit_tournament')
async def tournament_main_edit(callback: CallbackQuery):
    await callback.answer('')

    options = LinkPreviewOptions(
        is_disabled=True
    )
    async with get_db_readonly() as session:  # Используем контекстный менеджер
        editors_list = await f.output_edits_list(session)

    await callback.message.answer(f"<b>Тут происходит просмотр турниров и участников</b>\n\n• Если необходимо внести какие-либо изменения в турнир, свяжитесь с редактором(-ами) {editors_list}\n\nВыбери нужное 👇", parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=ks.main_edit_tournament)
    

@router.callback_query(F.data == 'tournament_info')
async def tournament_info(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        async with get_db() as session:  # Используем контекстный менеджер
            await f.check_ban_user(callback.from_user.id, session) # проверка на бан

        await state.update_data(coins=None)  # Устанавливаем `None` для обнуления монет
        await state.update_data(tournament_price_with_coins=None) # Устанавливаем `None` для обнуления стоимости турнира с учётом монет
        await state.update_data(remaining_coins=None) # Устанавливаем `None` для обнуления оставшихся монет после списания
        await state.update_data(division_level_user = None) # Устанавливаем `None` для обнуления выбранного дивизиона для участия в турнире повторно
        await state.update_data(selected_tournament = None) # Устанавливаем `None` для выбранного турнира
        user_id = callback.from_user.id
    
        async with get_db_readonly() as session:  # Используем контекстный менеджер

            tournaments = await bt.get_list_tournaments(session)  # Получаем актуальный список

            if not tournaments:
                await callback.message.answer(f'<b>Пусто</b> 🥲\n\nНам жаль, но в данный момент нет ни одного доступного турнира...', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
            else: 
                if user_id in EDITOR:
                    tournament_info_editor = bt.create_tournaments_keyboard_editor(tournaments)
                    await callback.message.answer(f"<b>Тут отображаются доступные турниры, в которых можно принять участие</b>\n\nДоступные турниры 👇", parse_mode=ParseMode.HTML, reply_markup=tournament_info_editor)
                elif user_id in ADMINS or user_id in MAIN_EDITOR:
                    tournament_info_admins = bt.create_tournaments_keyboard_admin(tournaments)
                    await callback.message.answer(f"<b>Тут отображаются доступные турниры, в которых можно принять участие</b>\n\nДоступные турниры 👇", parse_mode=ParseMode.HTML, reply_markup=tournament_info_admins)
                else:
                    tournament_info = bt.create_tournaments_keyboard(tournaments)

                    if os.path.exists("Tennis/img/tournament/tournament.jpg"):  # Проверка, есть ли файл
                        photo = FSInputFile("Tennis/img/tournament/tournament.jpg")  # Загружаем файл
                        await callback.message.answer_photo(photo, caption=f"<b>Тут отображаются доступные турниры, в которых можно принять участие</b>\n\nДоступные турниры 👇", parse_mode=ParseMode.HTML, reply_markup=tournament_info)
                    else:
                        await callback.message.answer(f"<b>Тут отображаются доступные турниры, в которых можно принять участие</b>\n\nДоступные турниры 👇", parse_mode=ParseMode.HTML, reply_markup=tournament_info)
    else:
        await f.check_subscription_message(callback)
                

@router.callback_query(F.data.startswith("tournament_out_bnt_"))
async def registration_on_tournaments(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')

    async with get_db_readonly() as session:  # Используем контекстный менеджер

        user_id = callback.from_user.id
        data = await state.get_data()
        
        if "tournament_out_bnt_" in callback.data:
            selected_tournament = callback.data.replace("tournament_out_bnt_", "")
        else:
            selected_tournament = data.get("selected_tournament")
        
        await state.update_data(selected_tournament = selected_tournament)  # Сохраняем выбранный турнир в состояние
        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if data.get("division_level_user"):
            user_division_level = int(data.get("division_level_user"))
        else:
            user_division_level = user.division_level

        # Получаем турнир
        tournament_data = (await session.scalars(select(Tournament).where(Tournament.name_tournament == selected_tournament))).first()
        # Запрос "зарегистрирован ли пользователь на выбранный им турнир?"
        user_in_tournament = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == user_id, TournamentPlayers.id_tournament == tournament_data.tournament_id))).all()
        # Запрос для подсчёта количества игроков в дивизионе игрока
        player_count = await session.scalar(select(func.count()).select_from(TournamentPlayers).join(User, TournamentPlayers.id_tg_user == User.tg_user_id).where(TournamentPlayers.id_tournament == tournament_data.tournament_id,User.division_level == user_division_level))
        
        levelTournament_list = list(map(int, tournament_data.division.split(",")))
        name_division = (await session.scalars(select(Division))).all()
        # Создаём словарь {division_id: name}, чтобы быстрее искать названия
        division_dict = {div.division_id: div.name_division for div in name_division}
        # Преобразуем список ID в список названий
        levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]

        tournament_lvl = ", ".join(levelTournament_names)

        if int(player_count) >= int(tournament_data.quantity_person):            
            await callback.message.answer(f'<b>Мест больше нет</b> 🥲\n\nНам жаль, но на турнир уже записаться нельзя...\nПроверь другие доступные турниры или дождись нового 😎', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
        # временное первое условие ! ! !
        # if int(user_division_level) == 3:      
        #     await callback.message.answer(f'<b>Мест больше нет</b> 🥲\n\nНам жаль, но на турнир уже записаться нельзя...\nПроверь другие доступные турниры или дождись нового 😎', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
        elif user_in_tournament and not data.get("division_level_user"):
            if len(user_in_tournament) == 1:
                await state.update_data(division_level_user = user.division_level)
                if user.division_level > 1:
                    await callback.message.answer(f'🚀 <b>Вы уже участвуете в турнире!</b>\n\nХотите записаться на этот же турнир и сыграть в ещё одном дивизионе? 🤔', parse_mode=ParseMode.HTML, reply_markup=kb.one_else_tournament)
                else:
                    await callback.message.answer(f'✅ <b>Вы уже участвуете в турнире!</b>\n\nОжидайте завершения регистрации других участников!', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
            else:
                await callback.message.answer(f'✅ <b>Вы уже участвуете в турнире!</b>\n\nОжидайте завершения регистрации других участников!', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
        elif user.ban_status == True:
            await callback.message.answer(f'❌ <b>Вы не можете участвовать в турнире из-за бана</b>\n\nНам жаль, но на этот турнир записаться нельзя...\nБан будет снят {user.end_date_ban} 😎', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
        elif user_division_level == None:
            await callback.message.answer(f'⚠️ <b>Дорогой пользователь, пока Вы не можете участвовать в турнире</b>\n\nДля начала Вам нужно получить дивизион. Этим уже занимаются наши главные редакторы\n\nБлагодарим за понимание!', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
        elif user_division_level not in levelTournament_list:
            await callback.message.answer(f'⚠️ <b>Вы не можете участвовать в турнире</b>\n\nК сожалению, этот турнир доступен только для дивизиона(-ов):\n{tournament_lvl}', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
        elif user_division_level in levelTournament_list:
            await callback.message.answer(f"{tournament_data.regulations}\n\n<b>ДЕТАЛИ ТУРНИРА</b> 🏆\n\n<b><i>Турнир \"{tournament_data.name_tournament.upper()}\"</i></b>\n💪 Дивизион: {tournament_lvl}\n🙋‍♂️ Количество участников: {tournament_data.quantity_person} чел.\n📆 Начало: {tournament_data.start_tournament}\n📆 Окончание: {tournament_data.end_tournament}\n💰 Стоимость участия: {tournament_data.price} бел.руб.", parse_mode=ParseMode.HTML, reply_markup=kb.reglament)
            await state.update_data(division_level_user = None)
        else:
            await callback.message.answer(f"❌ <b>Какая-то ошибка</b>\n\nПожалуйста, если вы видите это сообщение, свяжитесь с нами 🙋‍♂️ @sup_MM", parse_mode=ParseMode.HTML, reply_markup=kb.exit)


@router.callback_query(F.data == 'one_else_tournament')
async def one_else_tournament(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')

    data = await state.get_data()
    division_level_user = data.get("division_level_user")

    keyboard = await register_one_else_tournament_keyboard(division_level_user)
    await callback.message.answer(f"Выберите ещё один дивизион для участия 👇", parse_mode=ParseMode.HTML, reply_markup=keyboard)



async def register_one_else_tournament_keyboard(division):
    division = int(division)

    async with get_db_readonly() as session:  # Используем контекстный менеджер

        # if division == 1:
        #     division += 1
        #     else_division = (await session.scalars(select(Division).where(Division.division_id == division))).first()
        #     buttons = [
        #         [InlineKeyboardButton(text = else_division.name_division, callback_data = f'division_{else_division.division_id}')]
        #     ]
        # elif division == 5:
        #     division -= 1
        #     else_division = (await session.scalars(select(Division).where(Division.division_id == division))).first()
        #     buttons = [
        #         [InlineKeyboardButton(text = else_division.name_division, callback_data = f'division_{else_division.division_id}')]
        #     ]
        # else: 
        #     division_low = division - 1
        #     else_division_low = (await session.scalars(select(Division).where(Division.division_id == division_low))).first()
        
        #     division_hight = division + 1
        #     else_division_hight = (await session.scalars(select(Division).where(Division.division_id == division_hight))).first()

        #     buttons = [
        #         [InlineKeyboardButton(text = else_division_low.name_division, callback_data = f'division_{else_division_low.division_id}')],
        #         [InlineKeyboardButton(text = else_division_hight.name_division, callback_data = f'division_{else_division_hight.division_id}')]
        #     ]
        if division > 1:
            division -= 1
            else_division = (await session.scalars(select(Division).where(Division.division_id == division))).first()
            
            buttons = [
                [InlineKeyboardButton(text = else_division.name_division, callback_data = f'division_{else_division.division_id}')]
            ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data.startswith("division_"))
async def handle_one_else_level_buttons(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')      

    one_else_division = callback.data.replace("division_", "")
    await state.update_data(one_else_division = one_else_division)

    await registration_on_tournaments(callback, state)