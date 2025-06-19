import pytz
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from aiogram.enums import ParseMode
from aiogram import F, Router
from sqlalchemy import func
from config.config import MAIN_EDITOR, EDITOR, ADMINS

import keywords.kw_any as kb
import handlers.btn_tournaments as bt
import handlers.functions as f
import handlers.classes as cl

from config.db import session
from models.TournamentPlayers import TournamentPlayers
from models.Tournament import Tournament
from models.Division import Division
from models.Payment import Payment
from models.User import User


router = Router()


@router.callback_query(F.data == 'kassa')
async def kassa(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')
    await state.set_state(cl.FindUser.name_kassa)
    
    user_id = callback.from_user.id
    if user_id in MAIN_EDITOR or user_id in EDITOR or user_id in ADMINS:
        await callback.message.answer('<b>Тут вы можете внести в учёт наличную оплату игрока за турнир 💳</b>\n\nВведите <b>username</b> игрока 👇', parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer('Функция недоступна! Вы не главный редактор / редактор! ❌')
        await f.start_message(callback, bot)


@router.callback_query(F.data == 'find_users_for_kassa')
async def find_users_for_kassa(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')
    await state.set_state(cl.FindUser.name_kassa)
    
    user_id = callback.from_user.id
    if user_id in MAIN_EDITOR or user_id in EDITOR or user_id in ADMINS:
        await callback.message.answer('Введите <b>username</b> игрока 👇', parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer('Функция недоступна! Вы не главный редактор / редактор! ❌')
        await f.start_message(callback, bot)


@router.message(cl.FindUser.name_kassa)
async def find_name_kassa(message: Message, state:FSMContext):
    link_finder_user = message.text.lower()

    await state.set_state(None)

    if 'https://t.me/' not in link_finder_user:
        if '@' in link_finder_user:
            link_finder_user = link_finder_user.replace('@', '', 1)

        link_finder_user = 'https://t.me/' + link_finder_user

    options = LinkPreviewOptions(
        is_disabled=True
    )

    list_finder_user = [row[0] for row in session.query(User.link).all()]

    if link_finder_user in list_finder_user:
        user = session.query(User).filter_by(link = link_finder_user).first()
        await state.update_data(tg_user_id_kassa = user.tg_user_id)

        if user.division_level != None:
            name_division = session.query(Division).filter(Division.division_id == int(user.division_level)).first()
            division_lvl = name_division.name_division
        else:
            division_lvl = 'Не определён'
        
        await message.answer(f'<b>Найден пользователь {user.name_user} 🙋‍♂️</b>\n\nСсылка: {user.link}\nДивизион: {division_lvl}', parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.edit_kassa)
    else:
        await message.answer('Пользователь с таким <b>username</b> не найден!',parse_mode=ParseMode.HTML, reply_markup=kb.back_division)


@router.callback_query(F.data == 'set_new_check')
async def set_new_check(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')

    tournament_info_kassa_players = bt.create_tournaments_keyboard_players_kassa(bt.get_list_tournaments_players_kassa())
    await callback.message.answer('Выберите оплаченный турнир 👇', reply_markup=tournament_info_kassa_players)


@router.callback_query(F.data.startswith("kassa_players_"))
async def handle_level_buttons(callback: CallbackQuery, state: FSMContext, bot):
    await callback.answer('')      

    data = await state.get_data()
    id_finder_user = data.get("tg_user_id_kassa")

    selected_tournament = callback.data.replace("kassa_players_", "").replace("_kassa", "")  # Получаем название выбранного турнира
    await state.update_data(selected_tournament_kassa = selected_tournament)

    # Получаем турнир
    tournament_data = session.query(Tournament).filter(Tournament.name_tournament == selected_tournament).first()
    # Запрос "зареган ли юзер на выбранный им турнир?"
    user_in_tournament = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == id_finder_user, TournamentPlayers.id_tournament == tournament_data.tournament_id).all()
    # Запрос для подсчёта количества игроков
    player_count = session.query(func.count()).filter(TournamentPlayers.id_tournament == tournament_data.tournament_id).scalar()

    user = session.query(User).filter_by(tg_user_id = id_finder_user).first()

    levelTournament_list = list(map(int, tournament_data.division.split(",")))
    name_division = session.query(Division).all()
    # Создаём словарь {division_id: name}, чтобы быстрее искать названия
    division_dict = {div.division_id: div.name_division for div in name_division}
    # Преобразуем список ID в список названий
    levelTournament_names = [division_dict[i] for i in levelTournament_list if i in division_dict]

    tournament_lvl = ", ".join(levelTournament_names)

    if int(player_count) >= int(tournament_data.quantity_person):            
        await callback.message.answer(f'<b>Мест больше нет</b> 🥲\n\nНам жаль, но на турнир уже записаться нельзя...', parse_mode=ParseMode.HTML, reply_markup=kb.exit_kassa)
    elif user_in_tournament:
        await callback.message.answer(f'✅ <b>Пользователь уже участвует в выбранном турнире!</b>', parse_mode=ParseMode.HTML, reply_markup=kb.exit_kassa)
    elif user.ban_status == True:
        await callback.message.answer(f'❌ <b>Пользователь не может участвовать в турнире из-за бана</b>\n\nБан будет снят {user.end_date_ban} 😎', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    elif user.division_level == None:
        await callback.message.answer(f'⚠️ <b>Пользователь пока не может участвовать в турнире</b>\n\nДля начала ему нужно получить дивизион. Этим занимаются наши главные редакторы', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    elif user.division_level not in levelTournament_list:
        await callback.message.answer(f'⚠️ <b>Пользователь не может участвовать в турнире</b>\n\nК сожалению, этот турнир доступен только для дивизиона(-ов):\n{tournament_lvl}', parse_mode=ParseMode.HTML, reply_markup=kb.exit_kassa)
    elif user.division_level in levelTournament_list:
        await selected_tournament_kassa(callback, state, bot)
    else:
        await callback.message.answer(f"📋 <b>Какая-то ошибка</b>\n\nПожалуйста, если вы видите это сообщение, свяжитесь с нами 🙋‍♂️ @sup_MM", parse_mode=ParseMode.HTML, reply_markup=kb.exit)



@router.callback_query(F.data == 'selected_tournament_kassa')
async def selected_tournament_kassa(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    data = await state.get_data()
    selected_tournament = data.get("selected_tournament_kassa")
    tournament = session.query(Tournament).filter(Tournament.name_tournament == selected_tournament).first()

    user_id = callback.from_user.id

    payment_kassa = await create_payment_keyboard(user_id, tournament.price)
    await callback.message.answer(f'<b>Страница оплаты наличным расчётом</b> 💰\n\n🏆 <b>Турнир:</b> {tournament.name_tournament}\n💰 <b>Стоимость участия:</b> {tournament.price} бел.руб.', parse_mode=ParseMode.HTML, reply_markup=payment_kassa)




# Вывод кнопок для оплаты

async def create_payment_keyboard(user_id, price):
    
    if user_id in EDITOR or user_id in MAIN_EDITOR or user_id in ADMINS:
        buttons = [
            [InlineKeyboardButton(text = f'✅ Подтвердить получение {price} бел.руб.', callback_data='confirm_kassa')],
            [InlineKeyboardButton(text = '❌ Отменить и выйти', callback_data='start_message')]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    else:
        return False



@router.callback_query(F.data == 'confirm_kassa')
async def confirm_kassa(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    data = await state.get_data()
    user_id = callback.from_user.id
    id_finder_user = data.get("tg_user_id_kassa")
    selected_tournament = data.get("selected_tournament_kassa")

    tournament = session.query(Tournament).filter(Tournament.name_tournament == selected_tournament).first()

    if tournament:
        # Запрос "зарегистрирован ли пользователь на выбранный им турнир?"
        user_in_tournament = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == id_finder_user, TournamentPlayers.id_tournament == tournament.tournament_id).all()

        if not user_in_tournament:
            now_UTC = datetime.now(tz=pytz.utc)
            date = now_UTC + timedelta(minutes=180)

            try:
                check = Payment(id_tournament = tournament.tournament_id, id_tg_user = id_finder_user, price = tournament.price, salesman = user_id, date = date)
                session.add(check)
                player = TournamentPlayers(id_tournament = tournament.tournament_id, id_tg_user = id_finder_user)
                session.add(player)
                session.commit()

                print(f"Наличная оплата пользователя \"{id_finder_user}\" была внесена за турнир '{tournament.name_tournament}' в размере '{tournament.price}' бел.руб.")
                await callback.message.answer(f"✅ <b>Оплата подтверждена!</b>\n Пользователь стал участником турнира '{tournament.name_tournament}'!", parse_mode=ParseMode.HTML, reply_markup=kb.exit)
                
                message_text_send = f'<b>Спасибо за наличную оплату!</b> 💰\n\n🏆 <b>Турнир:</b> {tournament.name_tournament}\n💰 <b>Стоимость участия:</b> {tournament.price} бел.руб.'

                try:
                    await bot.send_message(chat_id=id_finder_user, text=message_text_send, parse_mode=ParseMode.HTML, reply_markup=kb.exit)
                except Exception as e:
                    print(f"❌ Не удалось отправить сообщение о наличной оплате пользователю с id: {id_finder_user} из-за ошибки: {e}")
            except Exception as e:
                session.rollback()
                await message.answer("<b>Произошла критическая ошибка!</b>\n\nОбратитесь в поддержку 🙋‍♂️ @mm_sup, мы устраним её!", parse_mode=ParseMode.HTML, reply_markup=kb.exit)
                raise e

        else:
            await callback.message.answer(f"❌ Пользователь уже зарегистрирован на турнир '{tournament.name_tournament}'!", reply_markup=kb.exit)
    else:
        print(f"ОШИБКА! Наличная оплата пользователя \"{id_finder_user}\" не была записана. Турнир не найден в БД!")  
    await state.clear()
