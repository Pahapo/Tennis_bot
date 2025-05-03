from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.enums import ParseMode
from aiogram import F, Router
from config.config import MAIN_EDITOR, ADMINS

import keywords.kw_any as kb
import handlers.functions as f
import handlers.start as st


router = Router()


@router.callback_query(F.data == 'fast_booking_court')
async def fast_booking_court(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    data = await state.get_data()
    user_id = data.get("user_id") # взяли из состояния, которое записалось при /start

    if await f.check_fast_user(user_id):
        await callback.message.answer('<b>Быстрое бронирование 🎾</b>\n\nЕсли вы новичок, используйте \"Обычное бронирование\"\nЕсли Вы часто или профессионально играете, Вам подойдёт этот вариант\n\n<b>Автоматическое бронирование обеспечит Вас кортом в любое время</b>. Вы не столкнётесь с проблемой занятого корта, ведь бронирование мы берём на себя!\n\n<b>3 ПРОСТЫХ ШАГА:</b>\n• Выбери дату\n• Выбери корт\n• Выбери время\n\n⚡️ Чтобы использовать \"<b>Быстрое бронирование 🎾</b>\" необходима подписка \"<b>Tennis PRO</b>\"\n\n⚡️ Воспользуйтесь бесплатной версией, чтобы протестировать возможности (доступна 1 раз)', parse_mode=ParseMode.HTML, reply_markup=kb.fast_booking_court)
    else:
        st.cmd_start()

# @router.callback_query(F.data == 'find_users_for_ban')
# async def find_users_for_ban(callback: CallbackQuery, state:FSMContext):
#     await callback.answer('')
#     await state.set_state(cl.FindUser.name_ban)
    
#     user_id = callback.from_user.id
#     if user_id in MAIN_EDITOR or user_id in ADMINS:
#         await callback.message.answer('Введите <b>username</b> игрока 👇', parse_mode=ParseMode.HTML)
#     else:
#         await callback.message.answer('Функция недоступна! Вы не главный редактор! ❌')
#         st.cmd_start()


# @router.message(cl.FindUser.name_ban)
# async def find_name(message: Message, state:FSMContext):
#     await state.update_data(name = message.text)
#     name_finder_user = message.text.lower()

#     if '@' in name_finder_user:
#         name_finder_user = name_finder_user.replace('@', '', 1)

#     name_finder_user = 'https://t.me/' + name_finder_user

#     options = LinkPreviewOptions(
#         is_disabled=True
#     )

#     list_finder_user = [row[0] for row in session.query(User.link).all()]

#     if name_finder_user in list_finder_user:
#         user = session.query(User).filter_by(link = name_finder_user).first()
#         await state.update_data(tg_user_id = user.tg_user_id)

#         division_lvl = ''

#         if user.division_level != None:
#             name_division = session.query(Division).filter(Division.division_id == int(user.division_level)).first()
#             division_lvl = name_division.name_division
#         else:
#             division_lvl = 'Не определён'

#         await message.answer(f'<b>Найден пользователь {user.name_user} 🙋‍♂️</b>\n\nСсылка: {user.link}\nДивизион: {division_lvl}', parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.edit_ban)
#     else:
#         await message.answer('Пользователь с таким <b>username</b> не найден!', parse_mode=ParseMode.HTML, reply_markup=kb.back_ban)


# @router.callback_query(F.data == 'set_new_ban')
# async def set_new_ban(callback: CallbackQuery, state:FSMContext):
#     await callback.answer('')
#     await state.set_state(cl.FindUser.period_ban)
#     await callback.message.answer('Введите количество дней, на которое хотите забанить пользователя (только число) 👇')


# @router.message(cl.FindUser.period_ban)
# async def find_name(message: Message, state:FSMContext):
#     await state.update_data(period_ban = int(message.text))
#     await state.set_state(cl.FindUser.reason_ban)
#     await message.answer('Опишите причину бана. (Этот текст увидит пользователь) 👇')


# @router.message(cl.FindUser.reason_ban)
# async def find_name(message: Message, state:FSMContext, bot):
#     await state.update_data(reason_ban = message.text)

#     data = await state.get_data()
#     name_finder_user = data.get("tg_user_id")
#     period_ban = int(data.get("period_ban"))
#     reason_ban = message.text

#     # Работа с датами
#     end_date_ban = datetime.today() + timedelta(days = period_ban)

#     user = session.query(User).filter_by(tg_user_id = name_finder_user).first()
    
#     if user:
#         user.ban_status = True
#         if user.end_date_ban != None:
#             end_date_ban = datetime.strptime(user.end_date_ban, "%d.%m.%Y") + timedelta(days = period_ban)
#             user.end_date_ban = end_date_ban.strftime("%d.%m.%Y")

#         user.end_date_ban = end_date_ban.strftime("%d.%m.%Y")

#         print(f"Пользователь '{user.name_user}' был забанен на {period_ban} дн. до {end_date_ban.strftime("%d.%m.%Y")}!")
#         await message.answer(f"✅ Пользователь '{user.name_user}' был забанен на {period_ban} дн. до {end_date_ban.strftime("%d.%m.%Y")}!", reply_markup=kb.back_ban)
#         session.commit() # Сохраняем изменения (фиксируем транзакцию)

#         message_text_send = f"<b>Дорогой {user.name_user}, мы вынуждены сообщить, что Вам выдан Бан!</b> ❌\n\n<b>Причина:</b> {reason_ban}\n\n<b>⏰ Окончание Бана:</b> {end_date_ban.strftime("%d.%m.%Y")}\n\n<i>Данное ограничение касается только участия в турнирах!</i>"

#         try:
#             await bot.send_message(chat_id=user.tg_user_id, text=message_text_send, parse_mode=ParseMode.HTML, reply_markup=kb.exit)
#         except Exception as e:
#             print(f"Не удалось отправить сообщение о бане пользователю с id: {user.tg_user_id} из-за ошибки: {e}")
#     else:
#         print(f"ОШИБКА! Пользователя '{user.name_user}' не был забанен!")  
#     await state.clear()