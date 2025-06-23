import os
import re
import pytz
import asyncio
import aiohttp
from aiogram.types import CallbackQuery, LinkPreviewOptions, FSInputFile
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram import F, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from config.config import ADMINS, MAIN_EDITOR, EDITOR

import keywords.kw_tournament as kb
import keywords.kw_payment as kp
import handlers.classes as cl
import handlers.functions as f
import googleSheet.googleSheet as gs

from config.db import session
from models.TournamentPlayers import TournamentPlayers
from models.Tournament import Tournament
from models.User import User
from models.Payment import Payment
from models.PaymentMethod import PaymentMethod
from models.Division import Division


router = Router()


@router.callback_query(F.data == 'reglament_confirm')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await state.set_state(cl.RegTournamentPlayerStates.level)
    payment_method = session.query(PaymentMethod).filter(PaymentMethod.payment_method_id == 1).first()

    if payment_method:
        data = await state.get_data()
        user_id = callback.from_user.id
        selected_tournament = data.get("selected_tournament")
        coins = data.get("coins")

        tournament = session.query(Tournament).filter(Tournament.name_tournament == selected_tournament).first()
        price = tournament.price
        if coins:
            price = round(price - coins / 100, 1)

        await state.update_data(tournament_price_with_coins = price)

        payment_address = await create_payment_keyboard(user_id, price)
        await callback.message.answer(f'<b>Страница оплаты по ЕРИП</b> 💳\n\n• Система \"Расчёт\" (ЕРИП)\n• Банковские, финансовые услуги\n• Банки, НКФО\n• {payment_method.bank_name}\n• Пополнение счёта\n\n<b>Введите номер счёта</b> 👇\n\n<pre><code>{payment_method.payment_method}</code></pre>\n\n💰 <b>Стоимость участия:</b> {price} бел.руб.\n\n• Если вы не успеете оплатить участие в турнире до истечения срока резервирования, оно аннулируется автоматически!\n\n⏰ <b>Время обработки платежа: 120 минут</b>', parse_mode=ParseMode.HTML, reply_markup=payment_address)
    else:
        await callback.message.answer(f'<b>Произошла ошибка загрузки страницы оплаты!</b> 💳\n\n• Пожалуйста, свяжитесь с поддержкой бота! Их контакт есть в описании бота', parse_mode=ParseMode.HTML, reply_markup=kb.exit)



# Вывод кнопок для оплаты

async def create_payment_keyboard(user_id, price):
    
    if user_id in EDITOR or user_id in MAIN_EDITOR or user_id in ADMINS:
        buttons = [
            [InlineKeyboardButton(text = f'✅ Я оплатил(-а) {price} бел.руб.', callback_data='confirm_payment')],
            [InlineKeyboardButton(text = '❌ Отменить и выйти', callback_data='start_message')]
        ]
    else:
        buttons = [
            [InlineKeyboardButton(text = f'✅ Я оплатил(-а) {price} бел.руб.', callback_data='confirm_payment')],
            [InlineKeyboardButton(text = 'Использовать монеты', callback_data='use_coins_q')],
            [InlineKeyboardButton(text = '❌ Отменить и выйти', callback_data='start_message')]
        ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)



@router.callback_query(F.data == 'confirm_payment')
async def confirm_payment(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')
    await state.set_state(cl.SendMessage.payment_flag) # если пользователь отправит фото вне этого состояния, оно не будет обработано
    
    await callback.message.answer('<b>Подтвердите оплату, отправив скриншот чека об оплате!</b> 👇', parse_mode=ParseMode.HTML, reply_markup=kp.confirm_payment_pl)
    await check_payment(callback, state, bot)


@router.message(F.content_type == types.ContentType.PHOTO, StateFilter(cl.SendMessage.payment_flag))
async def save_photo_payment(message: types.Message, state: FSMContext, bot):
    
    await state.set_state(None)
    
    await message.answer('<b>Спасибо за оплату!</b> 😎\n\n• Наши редакторы уже занимаются подтверждением Вашей транзакции! ⚡️ Ожидайте оповещения', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    
    data = await state.get_data()
    user_id = message.from_user.id
    user_name = message.from_user.full_name if message.from_user.username else message.from_user.username
    user = message.from_user
    if user.username:
        user_link = f"https://t.me/{user.username}"
    else:
        user_link = ""

    selected_tournament = data.get("selected_tournament")
    tournament_price_with_coins = data.get("tournament_price_with_coins")
    
    tournament = await find_tournament(selected_tournament)
    
    # Формируем базовое имя файла
    base_path = "Tennis/img/payment/"
    file_name = f"{user_id}_{tournament.tournament_id}.jpg"
    save_path = os.path.join(base_path, file_name)

    # Проверяем, существует ли уже файл, если да — добавляем номер копии
    copy_number = 1
    while os.path.exists(save_path):
        file_name = f"{user_id}_{tournament.tournament_id}_{copy_number}.jpg"
        save_path = os.path.join(base_path, file_name)
        copy_number += 1

    file = await message.bot.get_file(message.photo[-1].file_id)  # Получаем информацию о файле
    file_path = file.file_path  # Теперь `file_path` определён

    print(f"✅ Игроком с id {user_id} отправлен чек об оплате для участия в турнире {selected_tournament}. Чек: '{save_path}'")

    # Загружаем файл
    async with aiohttp.ClientSession() as session_http:
        async with session_http.get(f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}") as resp:
            if resp.status == 200:
                with open(save_path, "wb") as f:
                    f.write(await resp.read())
    
    now = datetime.now(tz=pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
    end_time = now + timedelta(minutes=120)
    end_time = end_time.strftime("%H:%M %d.%m")

    if tournament:
        coins = round(tournament.price - tournament_price_with_coins, 1)
        # НЕ ИЗМЕНЯТЬ СООБЩЕНИЕ ОТПРАВКИ РЕДАКТОРУ ! ! ! (это повлияет на функцию handle_button_click_confirm_payment)
        message_text_send = f"<b>Подтвердите оплату пользователя <a href='{user_link}'>{user_name}</a></b>\n\n• После подтверждения игрок станет участником турнира \"{selected_tournament}\"!\n\n💰 <b>Стоимость участия:</b> {tournament_price_with_coins} бел.руб.\n⏰ <b>Окончание подтверждения оплаты:</b> до {end_time}\n\n<tg-spoiler>🔗 <b>Чек оплаты:</b>\nID: {user_id}\nТурнир: {tournament.tournament_id}\nЦена: {tournament_price_with_coins}\nМонеты: {coins}\nЧек: {file_name}</tg-spoiler>"
    else:
        await message.answer("❌ Турнир не найден в базе данных! Игрок оплатил (проверить), но такой турнир не был найден в БД!")
        return

    # Отправляем скриншот редактору для проверки
    for editor in EDITOR:
        try:
            photo = FSInputFile(save_path)  # Локальный файл
            await bot.send_photo(chat_id=editor, photo=photo, caption=message_text_send, parse_mode=ParseMode.HTML, reply_markup=kp.confirm_payment)
        except Exception as e:
            print(f"❌ Не удалось отправить сообщение с чеком для оплаты пользователя с id: {user_id} из-за ошибки: {e}")



async def find_tournament(selected_tournament):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: session.query(Tournament).filter(Tournament.name_tournament == selected_tournament).first())



@router.callback_query(F.data == 'check_payment')
async def check_payment(callback: CallbackQuery, state:FSMContext, bot):

    data = await state.get_data()
    user_id = callback.from_user.id
    selected_tournament = data.get("selected_tournament")

    user_payment = ''

    for i in range(280):
        await asyncio.sleep(30)
        # Поиск id выбранного турнира
        selected_tournament = session.query(Tournament).filter(Tournament.name_tournament == data.get("selected_tournament")).first()
        # Запрос "оплатил ли пользователь выбранный турнир?"
        user_payment = session.query(Payment).filter(Payment.id_tg_user == user_id, Payment.id_tournament == selected_tournament.tournament_id).first()

        if user_payment:
            await success_payment(callback, state, bot)
            break

    # Ожидание оплаты 140 минут (120 + 20)
    if not user_payment:
        editors_list = await f.output_edits_list()

        options = LinkPreviewOptions(
            is_disabled=True
        )
        
        await callback.message.answer(f'<b>К сожалению, \"{selected_tournament.name_tournament}\" не был подтверждён или оплачен!</b> 😔\n\nНо мы уверены, что впереди у тебя ещё много побед и крутых турниров! 💪🎾\nИспользуй это время, чтобы набраться сил, усовершенствовать свою игру и вернуться ещё сильнее! 🚀🔥Ждём тебя в следующих соревнованиях!\n\n<i>• Если это ошибка, пожалуйста, свяжись с редактором(-ами) турнира!</i> {editors_list}', parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.exit)
        await state.clear()



@router.callback_query(F.data == 'handle_button_click_confirm_payment')
async def handle_button_click_confirm_payment(callback: types.CallbackQuery):

    message_text = callback.message.text or callback.message.caption  # Получаем текст сообщения
    match = re.search(r"ID: (\d+)\nТурнир: (\d+)\nЦена: ([\d\.]+)\nМонеты: ([\d\.]+)\nЧек: ([\w-]+)", message_text)  # Ищем нужные значения

    if match:
        user_id = match.group(1)        # ID пользователя
        tournament_id = match.group(2)  # ID турнира
        price = match.group(3)          # Цена
        coins = match.group(4)          # Монеты
        file_id = match.group(5)        # Чек (фото ID)

        now_UTC = datetime.now(tz=pytz.utc)
        date = now_UTC + timedelta(minutes=180)
        
        # Запрос "подтверждал ли этот турнир другой редактор?"
        user_payment = session.query(Payment).filter(Payment.id_tg_user == user_id, Payment.id_tournament == tournament_id).first()

        if not user_payment:
            check = Payment(id_tournament = tournament_id, id_tg_user = user_id, price = price, coins = coins, photo = file_id, date = date)
            try:
                session.add(check)
                session.commit()

                print(f"✅ Игрок с id {user_id} добавлен в таблицу 'Payment' после подтверждения оплаты")
                await callback.answer(f"✅ Оплата подтверждена", show_alert=False)
            except Exception as e:
                session.rollback()
                raise e

        await callback.answer(f"⚠️ Оплата уже была подтверждена другим редактором!", show_alert=False)
    else:
        print("❌ Данные не были обработаны при отправке сообщения с оплатой редактору за турнир!")

    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()



@router.callback_query(F.data == 'success_payment')
async def success_payment(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    data = await state.get_data()
    user_id = callback.from_user.id

    # Поиск id выбранного турнира
    selected_tournament = session.query(Tournament).filter(Tournament.name_tournament == data.get("selected_tournament")).first()
    # Запрос "зарегистрирован ли пользователь на выбранный им турнир?"
    user_in_tournament = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == user_id, TournamentPlayers.id_tournament == selected_tournament.tournament_id).all()

    selected_user = session.query(User).filter(User.tg_user_id == user_id).first()

    if data.get("one_else_division"):
        division_level = int(data.get("one_else_division"))
        await state.update_data(one_else_division = None)
    else:
        division_level = selected_user.division_level
        
    user_division = session.query(Division).filter(Division.division_id == division_level).first()

    if len(user_in_tournament) < 2:
        try:
            user = TournamentPlayers(id_tournament = selected_tournament.tournament_id, id_tg_user = user_id)
            session.add(user)

            if selected_user.coins:
                if data.get("coins"):
                    selected_user.coins -= data.get("coins")
                    print(f'✅ Игрок с id {selected_user.tg_user_id} применил {data.get("coins")} монет для участия в турнире - "{selected_tournament.name_tournament}"!')

            session.commit()
            
            print(f"✅ Игрок с id {selected_user.tg_user_id} зарегистрировался на турнир - '{selected_tournament.name_tournament}'!")
        except Exception as e:
            session.rollback()
            raise e


    await callback.message.answer('✅ <b>Регистрация на турнир подтверждена!</b>\n\nОжидайте завершения регистрации других участников', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    
    try:
        gs.addPlayerInList(selected_user.name_user, selected_user.link, selected_tournament.name_tournament, user_division.name_division)
        print(f"✅ Игрок добавлен в Excel после регистрации на турнир - '{selected_tournament.name_tournament}' в '{user_division.name_division}' дивизион!")
    except Exception as e:
        print(f"Excel не смог добавить пользователя с id {selected_user.tg_user_id} в турнир '{selected_tournament.name_tournament}' и дивизион '{user_division.name_division} 'из-за ошибки: {e}")
       
        # Отправляем редактору сообщение об ошибке добавления в Excel
        text_send = f"<b>Не получилось добавить пользователя {selected_user.name_user} в турнир '{selected_tournament.name_tournament}' в '{user_division.name_division}' дивизион из-за ошибки!</b>\n\nОбратитесь в поддержку 🙋‍♂️ @mm_sup"
        for editor in EDITOR:
            try:
                await bot.send_message(chat_id=editor, text=text_send, parse_mode=ParseMode.HTML, reply_markup=kb.exit)
            except Exception as e:
                print(f"Не удалось отправить редактору сообщение об ошибке при добавлении пользователя с id: {selected_user.tg_user_id} в Excel из-за ошибки: {e}")

    await state.clear()



@router.callback_query(F.data == 'confirm_error_payment')
async def confirm_error_payment(callback: CallbackQuery, state:FSMContext):
    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()

