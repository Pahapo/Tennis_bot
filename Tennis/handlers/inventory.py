from aiogram import F, Router
from aiogram.types import CallbackQuery

import handlers.functions as f

router = Router()


@router.callback_query(F.data == 'inventory')
async def inventory(callback: CallbackQuery, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        await callback.message.answer(f"inventory")
    else:
        await f.check_subscription_message(callback)