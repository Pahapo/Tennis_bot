import asyncio
from aiogram.types import Message, LinkPreviewOptions, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram import Router
from handlers.functions import adm_start_t, m_edit_start_t, edit_start_t, all_players_start_t
from config.config import CHANNEL, ADMINS, MAIN_EDITOR, EDITOR

import keywords.kw_start as kb
import handlers.functions as f
import handlers.referrals as r


router = Router()  # Создаем роутер


@router.message(CommandStart())  # Создали декоратор для обработки поступающих сообщений
async def cmd_start(message: Message, bot):

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

    args = message.text.split()
    await r.check_referral(args, user_id, bot) # реферальная система
    
    await f.save_user(user_id, user_name, user_link.lower(), message)

    if user_id in ADMINS:
        await message.answer(adm_start_t, parse_mode=ParseMode.HTML, reply_markup=kb.main_admin_btn)
    elif user_id in MAIN_EDITOR:
        await message.answer(f"<b>Уважаемый {user_name}!</b> 👋\n\n{m_edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.main_edit_btn)
    elif user_id in EDITOR:
        await message.answer(f"<b>Уважаемый {user_name}!</b> 👋\n\n{edit_start_t}", parse_mode=ParseMode.HTML, reply_markup=kb.edit_btn)
    else:
        keyboard = await f.create_tournament_table_keyboard_user(user_id)
        await message.answer(f"<b>Привет {user_name}!</b> 👋\n\n{all_players_start_t}", parse_mode=ParseMode.HTML, link_preview_options=options, reply_markup=keyboard)