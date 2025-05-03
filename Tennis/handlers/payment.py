import os
import re
import pytz
import asyncio
import aiohttp
from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram import F, Router, types
from datetime import datetime, timedelta


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
from models.Division import Division
from config.config import CARD_NUMBER, EDITOR


router = Router()

@router.callback_query(F.data == 'reglament_confirm')
async def register(callback: CallbackQuery, state:FSMContext): # доделать с оплатой!!!
    await callback.answer('')
    await state.set_state(cl.RegTournamentPlayerStates.level)
    await callback.message.answer(f'<b>Страница оплаты по ЕРИП</b> 💳\n\n• Система \"Расчёт\" (ЕРИП)\n• Банковские, финансовые услуги\n• Банки, НКФО\n• Альфабанк\n• Пополнение счёта\n\n<b>Введите номер счёта</b> 👇\n\n<pre><code>{CARD_NUMBER}</code></pre>\n\n• Если вы не усеете оплатить участие в турнире до истечения срока резервирования, оно аннулируется автоматически!\n\n⏰ <b>Время: 120 минут</b>', parse_mode=ParseMode.HTML, reply_markup=kb.payment_address)


@router.callback_query(F.data == 'confirm_payment')
async def confirm_payment(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await callback.message.answer('<b>Подтвердите оплату, отправив скриншот чека об оплате!</b> 👇', parse_mode=ParseMode.HTML, reply_markup=kb.confirm_payment_pl)
    await check_payment(callback, state)


@router.message(F.content_type == types.ContentType.PHOTO)    # КАК НЕ ПОЛУЧАТЬ ФОТО ИЗ ЛЮБОГО МЕСТА, А ТОЛЬКО ПРИ ОТПРАВКЕ ЧЕКА?
async def save_photo_payment(message: types.Message, state: FSMContext, bot):
    
    await message.answer('После подтверждения оплаты вы станете участником турнира!', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    
    data = await state.get_data()
    user_id = data.get("user_id")
    user_name = data.get("user_name")
    user_link = data.get("user_link")
    selected_tournament = data.get("selected_tournament")
    
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

    print(f"✅ Игроком с id {user_id} отправлен чек об оплате для участия в турнире {selected_tournament}. Чек: `{save_path}`")

    # Загружаем файл
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}") as resp:
            if resp.status == 200:
                with open(save_path, "wb") as f:
                    f.write(await resp.read())
    
    now = datetime.now(tz=pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
    end_time = now + timedelta(minutes=120)
    end_time = end_time.strftime("%H:%M %d.%m")

    if tournament:
        message_text_send = f"<b>Подтверждение оплаты пользователя <a href='{user_link}'>{user_name}</a></b>\n\n• После подтверждения игрок станет участником турнира \"{selected_tournament}\"!\n\n⏰ <b>Дата окончания оплаты:</b> до {end_time}\n\n🔗 <b>Чек оплаты:</b>\nID: {user_id}\nТурнир: {tournament.tournament_id}\nЦена: {tournament.price}\nЧек: {file_name}"
    else:
        await message.answer("❌ Турнир не найден в базе данных! Игрок оплатил, но такой турнир не был найден в БД!")
        return

    # Отправляем скриншот редактору для проверки
    for editor in EDITOR:
        try:
            photo = FSInputFile(save_path)  # Локальный файл
            # НЕ ИЗМЕНЯТЬ СООБЩЕНИЕ ОТПРАВКИ РЕДАКТОРУ ! ! ! (это повлияет на функцию handle_button_click_confirm_payment)
            await bot.send_photo(chat_id=editor, photo=photo, caption=message_text_send, parse_mode=ParseMode.HTML, reply_markup=kp.confirm_payment)
        except Exception as e:
            print(f"Не удалось отправить сообщение с чеком для оплаты пользователя с id: {user_id} из-за ошибки: {e}")



async def find_tournament(selected_tournament):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: session.query(Tournament).filter(Tournament.name_tournament == selected_tournament).first())



@router.callback_query(F.data == 'check_payment')
async def check_payment(callback: CallbackQuery, state:FSMContext):

    data = await state.get_data()
    selected_tournament = data.get("selected_tournament")

    user_payment = ''

    for i in range(280):
        await asyncio.sleep(30)
        # Поиск id выбранного турнира
        selected_tournament = session.query(Tournament).filter(Tournament.name_tournament == data.get("selected_tournament")).first()
        # Запрос "оплатил ли пользователь выбранный турнир?"
        user_payment = session.query(Payment).filter(Payment.id_tg_user == data.get("user_id"), Payment.id_tournament == selected_tournament.tournament_id).first()

        if user_payment:
            await success_payment(callback, state)
            break

    # Ожидание оплаты 140 минут (120 + 20)
    if not user_payment:
        editors_list = await f.output_edits_list()

        options = LinkPreviewOptions(
            is_disabled=True
        )
        
        await callback.message.answer(f'<b>К сожалению, \"{selected_tournament.name_tournament}\" не был оплачен!</b> 😔\n\nНо мы уверены, что впереди у тебя ещё много побед и крутых турниров! 💪🎾\nИспользуй это время, чтобы набраться сил, усовершенствовать свою игру и вернуться ещё сильнее! 🚀🔥Ждём тебя в следующих соревнованиях!\n\n<i>• Если это ошибка, пожалуйста, свяжитесь с редактором(-ами) турнира!</i> {editors_list}', parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.exit)
        await state.clear()



@router.callback_query(F.data == 'handle_button_click_confirm_payment')
async def handle_button_click_confirm_payment(callback: types.CallbackQuery):

    message_text = callback.message.text or callback.message.caption  # Получаем текст сообщения
    match = re.search(r"ID: (\d+)\nТурнир: (\d+)\nЦена: (\d+)\nЧек: ([\w-]+)", message_text)  # Ищем нужные значения

    if match:
        tournament_id = match.group(2)  # ID турнира
        user_id = match.group(1)        # ID пользователя
        price = match.group(3)          # Цена
        file_id = match.group(4)        # Чек (фото ID)
        
        user = Payment(id_tournament = tournament_id, id_tg_user = user_id, price = price, photo = file_id)
        session.add(user)
        session.commit()

        print(f"Игрок {user_id} добавлен в таблицу 'Payment' после подтверждения оплаты")
        await callback.answer(f"✅ Оплата подтверждена", show_alert=False)
    else:
        print("❌ `user_id` не найден в сообщении при отправке сообщения с оплатой редактору за турнир!")

    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()



@router.callback_query(F.data == 'success_payment')
async def success_payment(callback: CallbackQuery, state:FSMContext):

    data = await state.get_data()

    # Поиск id выбранного турнира
    selected_tournament = session.query(Tournament).filter(Tournament.name_tournament == data.get("selected_tournament")).first()
    # Запрос "зарегистрирован ли пользователь на выбранный им турнир?"
    user_in_tournament = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == data.get("user_id"), TournamentPlayers.id_tournament == selected_tournament.tournament_id).all()

    selected_user = session.query(User).filter(User.tg_user_id == data.get("user_id")).first()
    user_division = session.query(Division).filter(Division.division_id == selected_user.division_level).first()

    if not user_in_tournament:
        user = TournamentPlayers(id_tournament = selected_tournament.tournament_id, id_tg_user = data.get("user_id"))
        session.add(user)
        session.commit()
        print(f"Игрок {selected_user.tg_user_id} зарегистрировался на турнир - '{selected_tournament.name_tournament}'!")

    await callback.message.answer('✅ <b>Регистрация на турнир подтверждена!</b>\n\nОжидайте завершения регистрации других участников', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    
    gs.addPlayerInList(selected_user.name_user, selected_user.link, selected_tournament.name_tournament, user_division.name_division)
    print(f"Добавление игрока в Excel для регистрации на турнир - '{selected_tournament.name_tournament}' произошло успешно!")
    await state.clear()



@router.callback_query(F.data == 'confirm_error_payment')
async def confirm_error_payment(callback: CallbackQuery, state:FSMContext):
    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()