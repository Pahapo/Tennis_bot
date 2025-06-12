import os
import aiohttp
from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.filters import StateFilter
from config.config import ADMINS

import keywords.kw_send_message as kb
import keywords.kw_any as ka
import handlers.classes as cl
import handlers.functions as f

from config.db import session
from models.User import User

router = Router()


@router.callback_query(F.data == 'sending_messages')
async def register(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    user_id = callback.from_user.id
    if user_id in ADMINS:
        await callback.message.answer('Для начала выбери, какое сообщение ты хочешь отправить: с фото или без него?', reply_markup=kb.send_message_photo_q)
    else:
        await callback.message.answer('Функция недоступна! Вы не админ! ❌')
        await f.start_message(callback, bot)



# Отправка сообщения с текстом


@router.callback_query(F.data == 'sending_messages_text')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await state.set_state(cl.SendMessage.message)
    await callback.message.answer('Введи сообщение, которое хочешь разослать (только текст) 👇')

@router.message(cl.SendMessage.message)
async def sending_messages(message: Message, state:FSMContext):    
    await state.update_data(message_text_send = message.html_text)

    await state.set_state(None)

    options = LinkPreviewOptions(
        is_disabled=True
    )

    await message.answer(f"<b>Текст для рассылки:</b>\n\n{message.html_text}", parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.send_message_war)



# Отправка сообщения с фото и текстом


def escape_markdown(text: str) -> str:
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)


@router.callback_query(F.data == 'sending_messages_photo')
async def register(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await state.set_state(cl.SendMessage.message_flag)
    await callback.message.answer('Введи сообщение, которое хочешь разослать, прикрепив фото 👇')


@router.message(F.content_type == types.ContentType.PHOTO, StateFilter(cl.SendMessage.message_flag))
async def save_photo_payment(message: types.Message, state: FSMContext):

    await state.set_state(None)

    if message.caption:
        # Сохраняем оригинальный текст без экранирования
        await state.update_data(message_text_send=message.html_text if message.html_text else message.caption)
        message_text_send = message.html_text if message.html_text else message.caption

    # Формируем базовое имя файла
    base_path = "Tennis/img/message/"
    file_name = "message.jpg"
    save_path = os.path.join(base_path, file_name)

    file = await message.bot.get_file(message.photo[-1].file_id)
    file_path = file.file_path

    # Загружаем файл
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.telegram.org/file/bot{message.bot.token}/{file_path}") as resp:
            if resp.status == 200:
                with open(save_path, "wb") as f:
                    f.write(await resp.read())
    
    photo = FSInputFile(save_path)

    options = LinkPreviewOptions(
        is_disabled=True
    )
    
    if message.caption:
        await message.answer_photo(photo, caption=message_text_send, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.send_message_war)
    else:
        await message.answer_photo(photo, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.send_message_war)


# Подтверждение для начала рассылки


@router.callback_query(F.data == 'send_war')
async def send_war(callback: CallbackQuery, bot):
    await callback.answer('')
    await callback.message.answer("<b>Подтверди</b>, чтобы начать рассылку 👇", parse_mode=ParseMode.HTML, reply_markup=kb.send_message)


@router.callback_query(F.data == 'send')
async def send(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    options = LinkPreviewOptions(
        is_disabled=True
    )
    
    user_id = callback.from_user.id
    if user_id in ADMINS:

        data = await state.get_data()
        message_text_send = data.get("message_text_send")

        users = [row[0] for row in session.query(User.tg_user_id).all()]
        count_send_message = 0

        # Проверяем файл Tennis/img/message/message.jpg
        base_path = "Tennis/img/message/"
        file_name = "message.jpg"
        save_path = os.path.join(base_path, file_name)

        if users:            
            for user_id in users:
                try:
                    # Проверяем, есть ли фото
                    if os.path.exists(save_path):
                        if message_text_send:
                            photo = FSInputFile(save_path)  # Локальный файл
                            await bot.send_photo(chat_id=user_id, photo=photo, caption=message_text_send, parse_mode=ParseMode.HTML, reply_markup=ka.exit)
                        else:
                            photo = FSInputFile(save_path)  # Локальный файл
                            await bot.send_photo(chat_id=user_id, photo=photo, parse_mode=ParseMode.HTML, reply_markup=ka.exit)
                    else:
                        await bot.send_message(chat_id=user_id, text=message_text_send, link_preview_options=options, disable_web_page_preview=True, parse_mode=ParseMode.HTML, reply_markup=ka.exit)
                    
                    count_send_message += 1

                except Exception as e:
                    print(f"❌ Не удалось отправить сообщение при рассылке пользователю с id: {user_id} из-за ошибки: {e}")
            
            await callback.message.answer(f"✅ <b>Рассылка завершена!</b>\n\nСообщение получило {count_send_message} чел.", parse_mode=ParseMode.HTML, reply_markup=ka.exit)
        else:
            await callback.message.answer("Пользователей ещё нет 📂, добавь хотя бы одного для теста!", reply_markup=ka.exit)

        # Проверяем, существует ли фото, и удаляем её
        if os.path.exists(save_path):
            os.remove(save_path)

    else:
        await callback.message.answer('Функция недоступна! Вы не админ! ❌', reply_markup=ka.exit)
        await f.start_message(callback, bot)
    await state.clear()


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
    #                 print(f"❌ Не удалось отправить сообщение пользователю с name: {user_name} из-за ошибки: {e}")     # ИЗМЕНИТЬ user_name
    #     except FileNotFoundError:
    #         await callback.message.answer("Пользователей ещё нет 📂, добавь хотя бы одного!")
    # else:
    #     await callback.message.answer('Функция недоступна! Вы не админ! ❌')