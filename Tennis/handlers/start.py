import asyncio
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram import Router

import keywords.kw_start as kb
import handlers.functions as f
import handlers.referrals as r


router = Router()  # Создаем роутер


@router.message(CommandStart())  # Создали декоратор для обработки поступающих сообщений
async def cmd_start(message: Message, state:FSMContext, bot):

    user_name = message.from_user.full_name if message.from_user.username else message.from_user.username
    user_id = message.from_user.id
    user = message.from_user
    if user.username:
        user_link = f"https://t.me/{user.username}"
    else:
        user_link = ""

    args = message.text.split()
    await r.check_referral(args, user_id, bot) # реферальная система
    await f.save_user(user_id, user_name, user_link.lower(), message, state)
