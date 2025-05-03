from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from config.config import ADMINS

import keywords.kw_send_message as kb
import keywords.kw_any as ka
import handlers.classes as cl
import handlers.start as st

from config.db import session
from models.User import User

router = Router()

message_text_send = ''


@router.callback_query(F.data == 'sending_messages')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')

    user_id = callback.from_user.id
    if user_id in ADMINS:
        await state.set_state(cl.SendMessage.message)
        await callback.message.answer('Введи сообщение, которое хочешь разослать (только текст) 👇')
    else:
        await callback.message.answer('Функция недоступна! Вы не админ! ❌')
        st.cmd_start()
    

@router.message(cl.SendMessage.message)
async def sending_messages(message: Message, state:FSMContext):    
    await state.update_data(message = message.html_text)

    options = LinkPreviewOptions(
        is_disabled=True
    )

    data = await state.get_data()
    global message_text_send
    message_text_send = data.get("message")

    await message.answer(f"<b>Текст для рассылки:</b>\n\n{message_text_send}", parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.send_message_war)
    await state.clear()


@router.callback_query(F.data == 'send_war')
async def send(callback: CallbackQuery, bot):
    await callback.answer('')
    await callback.message.answer("<b>Подтверди</b>, чтобы начать рассылку 👇", parse_mode=ParseMode.HTML, reply_markup=kb.send_message)


@router.callback_query(F.data == 'send')
async def send(callback: CallbackQuery, bot):
    await callback.answer('')

    options = LinkPreviewOptions(
        is_disabled=True
    )
    
    user_id = callback.from_user.id
    if user_id in ADMINS:

        users = [row[0] for row in session.query(User.tg_user_id).all()]
        count_send_message = 0

        if users:            
            for user_id in users:
                try:
                    await bot.send_message(chat_id=user_id, text=message_text_send, link_preview_options=options, disable_web_page_preview=True, parse_mode=ParseMode.HTML, reply_markup=ka.exit)
                    count_send_message +=1

                except Exception as e:
                    print(f"Не удалось отправить сообщение при рассылке пользователю с id: {user_id} из-за ошибки: {e}")
            await callback.message.answer(f"✅ <b>Рассылка завершена!</b>\n\nСообщение получило {count_send_message} чел.", parse_mode=ParseMode.HTML, reply_markup=ka.exit)
        else:
            await callback.message.answer("Пользователей ещё нет 📂, добавь хотя бы одного для теста!", reply_markup=ka.exit)
    else:
        await callback.message.answer('Функция недоступна! Вы не админ! ❌', reply_markup=ka.exit)
        st.cmd_start()


@router.callback_query(F.data == 'send_winners')
async def send_winner(callback: CallbackQuery, bot):
    await callback.answer('')


    # user_id = callback.from_user.id
    # if user_id in ADMINS:
    #     try:
    #         # Читаем существующие данные из файла
    #         with open("users_winner.json", "r", encoding="utf-8") as file:        # ИЗМЕНИТЬ ПОД ЧТЕНИЕ ИЗ БД ПОБЕДИТЕЛЕЙ ТУРНИРОВ
    #             users_winner = json.load(file)                                    # ДОБАВИТЬ В ТАБЛИЦУ В БД СТОЛБЕЦ С ПОБЕДИТЕЛЯМИ И ИХ МЕСТАМИ


    #         # достать: user_name, user_id, name_turnament, place_on_tumnaments
        

    #         for user in users_winner:         # ИЗМЕНИТЬ ИЕРАРХИЮ ПОИСКА ID И МЕСТА
    #             try:
    #                 if user.place == 1:
    #                     message_text_send = f'<b>Поздравляем с Победой 🎉 в турнире "{name_turnament}", Вы заняли "1-е место" место🏆!</b>\n\n<b>Золото</b> - показатель блестящей победы! Ваше мастерство, упорство и страсть к игре вдохновляют. Пусть этот триумф станет началом новых высот! 🏆🎾' 
    #                     await bot.send_message(chat_id=user, text='🏆', parse_mode=ParseMode.HTML)
    #                     await bot.send_message(chat_id=user, text=message_text_send, parse_mode=ParseMode.HTML, reply_markup=ka.exit)
    #                 elif user.place == 2:
    #                     message_text_send = f'<b>Поздравляем с Победой 🎉 в турнире "{name_turnament}", Вы заняли "2-е место" место🏆!</b>\n\n<b>Серебро</b> - доказательство вашего таланта и силы духа! Гордитесь собой, ведь вы подарили нам незабываемый матч. Вперёд к новым вершинам! 💪🌟' 
    #                     await bot.send_message(chat_id=user, text='🏆', parse_mode=ParseMode.HTML)
    #                     await bot.send_message(chat_id=user, text=message_text_send, parse_mode=ParseMode.HTML, reply_markup=ka.exit)
    #                 elif user.place == 3:
    #                     message_text_send = f'<b>Поздравляем с Победой 🎉 в турнире "{name_turnament}", Вы заняли "3-е место" место🏆!</b>\n\n<b>Бронза</b> - это ступень к великим победам! Ваш труд и преданность не остались незамеченными. Продолжайте заряжать корт своей энергией! 🥉🔥'
    #                     await bot.send_message(chat_id=user, text='🏆', parse_mode=ParseMode.HTML)
    #                     await bot.send_message(chat_id=user, text=message_text_send, parse_mode=ParseMode.HTML, reply_markup=ka.exit)
    #             except Exception as e:
    #                 print(f"Не удалось отправить сообщение пользователю с name: {user_name} из-за ошибки: {e}")     # ИЗМЕНИТЬ user_name
    #     except FileNotFoundError:
    #         await callback.message.answer("Пользователей ещё нет 📂, добавь хотя бы одного!")
    # else:
    #     await callback.message.answer('Функция недоступна! Вы не админ! ❌')