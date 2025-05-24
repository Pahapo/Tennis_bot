import asyncio
from aiogram.types import Message, LinkPreviewOptions, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram import Router
from config.config import CHANNEL, ADMINS, MAIN_EDITOR, EDITOR

import keywords.kw_start as kb
import handlers.functions as f
from handlers.functions import adm_start_t, m_edit_start_t, edit_start_t, all_players_start_t


router = Router()  # Создаем роутер


@router.message(CommandStart())  # Создали декоратор для обработки поступающих сообщений
async def cmd_start(message: Message, state: FSMContext):

    user_name = message.from_user.full_name if message.from_user.username else message.from_user.username
    user_id = message.from_user.id
    user = message.from_user
    if user.username:
        user_link = f"https://t.me/{user.username}"
    else:
        user_link = ""

    options = LinkPreviewOptions(
        url=CHANNEL,
        prefer_small_media=True
    )

    await state.update_data(user_id = user_id)  # Сохраняем user_id в состояние
    await state.update_data(user_name = user_name)  # Сохраняем user_name в состояние
    await state.update_data(user_link = user_link)  # Сохраняем user_link в состояние
    await f.save_user(user_id, user_name, user_link.lower())

    if user_id in ADMINS:
        await message.answer(adm_start_t, parse_mode=ParseMode.HTML, reply_markup=kb.main_admin_btn)
    elif user_id in MAIN_EDITOR:
        await message.answer(f"<b>Уважаемый {user_name}!</b> 👋\n\n{m_edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.main_edit_btn)
    elif user_id in EDITOR:
        await message.answer(f"<b>Уважаемый {user_name}!</b> 👋\n\n{edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.edit_btn)
    else:
        
        # СКАЗКА (~30 секунд)

        story = await message.answer(f"Привет <b>{user_name}!</b> 👋", parse_mode=ParseMode.HTML)  # Сохраняем отправленное сообщение
        await asyncio.sleep(2)
        await story.edit_text("Давай я расскажу тебе 1 историю... 🎾")
        await asyncio.sleep(2.5)
        await story.edit_text("Где-то в далёком-придалёком королевстве 👑")
        await asyncio.sleep(2.5)
        await story.edit_text("Среди замков и драконов")
        await asyncio.sleep(1.9)
        await story.edit_text("Основался легендарный теннисный клуб! 🛡️")
        await asyncio.sleep(2.5)
        await story.edit_text("Только самые смелые выходили на корт ⚡️")
        await asyncio.sleep(2.5)
        await story.edit_text("Их ждали великие дуэли, турниры и таинственные награды...")
        await asyncio.sleep(3)
        await story.edit_text("Хочешь очутиться в далёком-придалёком королевстве? 🐉")
        await asyncio.sleep(2.8)
        await story.edit_text("Сразиться с соперниками?!")
        await asyncio.sleep(2)
        await story.edit_text("Выиграть турнир?! 🏆")
        await asyncio.sleep(2)
        await story.edit_text("Стать теннисным лордом?! 👑")
        await asyncio.sleep(2.1)
        await story.edit_text("<b>Пора начинать наше приключение!</b> 🚀", parse_mode=ParseMode.HTML)
        await asyncio.sleep(2.3)
        await story.edit_text("Корт ждёт героя, готового вписать своё имя в историю! 🎾")
        await asyncio.sleep(3.2)
        await story.delete()

        await message.answer(f"<b>Привет {user_name}!</b> 👋\n\n{all_players_start_t}", parse_mode=ParseMode.HTML, link_preview_options=options, reply_markup=f.create_tournament_table_keyboard(user_id))
