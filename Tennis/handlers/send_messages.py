import json
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from config import ADMINS

import handlers.keywords as kb
import handlers.classes as cl
import handlers.start as st

router = Router()

message_text_send = ''


@router.callback_query(F.data == 'sending_messages')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать

    user_id = callback.from_user.id
    if user_id in ADMINS:
        await state.set_state(cl.SendMessage.message)
        await callback.message.answer('Хозяин, введи пост, который хочешь разослать (только текст) 👇')
    else:
        await callback.message.answer('Функция недоступна! Вы не админ! 🚫')
        st.cmd_start()
    

@router.message(cl.SendMessage.message)
async def sending_messages(message: Message, state:FSMContext):    
    await state.update_data(message = message.text)

    data = await state.get_data()
    global message_text_send
    message_text_send = data.get("message")

    await message.answer(f"<b>Текст для рассылки:</b>\n\n{message_text_send}", parse_mode=ParseMode.HTML, reply_markup=kb.send_message_war)
    await state.clear()


@router.callback_query(F.data == 'send_war')
async def send(callback: CallbackQuery, bot):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    await callback.message.answer("<b>Подтверди</b>, чтобы начать рассылку 👇", parse_mode=ParseMode.HTML, reply_markup=kb.send_message)


@router.callback_query(F.data == 'send')
async def send(callback: CallbackQuery, bot):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    
    user_id = callback.from_user.id
    if user_id in ADMINS:
        try:
            # Читаем существующие данные из файла
            with open("users.json", "r", encoding="utf-8") as file:
                users = json.load(file)
            
            for user_id in users:
                try:
                    await bot.send_message(chat_id=user_id, text=message_text_send, parse_mode=ParseMode.HTML)
                except Exception as e:
                    print(f"Не удалось отправить сообщение пользователю с id: {user_id} из-за ошибки: {e}")
        except FileNotFoundError:
            await callback.message.answer("Пользователей ещё нет 📂, добавь хотя бы одного для теста!")
    else:
        await callback.message.answer('Функция недоступна! Вы не админ! 🚫')


@router.callback_query(F.data == 'send_winners')
async def send(callback: CallbackQuery, bot):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    
    user_id = callback.from_user.id
    if user_id in ADMINS:
        try:
            # Читаем существующие данные из файла
            with open("users_winner.json", "r", encoding="utf-8") as file:        # ИЗМЕНИТЬ НАЗВАНИЕ ФАЙЛА
                users_winner = json.load(file)


            # достать: user_name, user_id, name_turnament, place_on_tumnaments
        

            for user in users_winner:         # ИЗМЕНИТЬ ИЕРАРЗИЮ ПОИСКА ID И МЕСТА
                try:
                    if user.place == 1:
                        message_text_send = f'<b>Поздравляем с Победой 🎉 в турнире "{name_turnament}", Вы заняли "НОМЕР" место🏆!</b>\n\n<b>1-е место:</b>\n<b>Золото</b> - показатель блестящей победы! Ваше мастерство, упорство и страсть к игре вдохновляют. Пусть этот триумф станет началом новых высот! 🏆🎾' 
                        await bot.send_message(chat_id=user, text='🏆', parse_mode=ParseMode.HTML)
                        await bot.send_message(chat_id=user, text=message_text_send, parse_mode=ParseMode.HTML)
                    elif user.place == 2:
                        message_text_send = f'<b>Поздравляем с Победой 🎉 в турнире "{name_turnament}", Вы заняли "НОМЕР" место🏆!</b>\n\n<b>2-е место:</b>\n<b>Серебро</b> - доказательство вашего таланта и силы духа! Гордитесь собой, ведь вы подарили нам незабываемый матч. Вперёд к новым вершинам! 💪🌟' 
                        await bot.send_message(chat_id=user, text='🏆', parse_mode=ParseMode.HTML)
                        await bot.send_message(chat_id=user, text=message_text_send, parse_mode=ParseMode.HTML)
                    elif user.place == 3:
                        message_text_send = f'<b>Поздравляем с Победой 🎉 в турнире "{name_turnament}", Вы заняли "НОМЕР" место🏆!</b>\n\n<b>3-е место:</b>\n<b>Бронза</b> - это ступень к великим победам! Ваш труд и преданность не остались незамеченными. Продолжайте заряжать корт своей энергией! 🥉🔥'
                        await bot.send_message(chat_id=user, text='🏆', parse_mode=ParseMode.HTML)
                        await bot.send_message(chat_id=user, text=message_text_send, parse_mode=ParseMode.HTML)
                except Exception as e:
                    print(f"Не удалось отправить сообщение пользователю с name: {user_name} из-за ошибки: {e}")     # ИЗМЕНИТЬ user_name
        except FileNotFoundError:
            await callback.message.answer("Пользователей ещё нет 📂, добавь хотя бы одного!")
    else:
        await callback.message.answer('Функция недоступна! Вы не админ! 🚫')