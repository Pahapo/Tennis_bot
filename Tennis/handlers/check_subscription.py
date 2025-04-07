from aiogram import F, Router
from aiogram.types import CallbackQuery

import handlers.functions as f

router = Router()

@router.callback_query(F.data == "check_subscription")  # Обработка нажатия на кнопку "Я подписался"
async def check_subscription_callback(callback: CallbackQuery, bot):

    # Повторная проверка подписки
    if await f.check_subscription(callback.from_user.id, bot):
        await callback.answer("Спасибо за подписку!")

        await f.start_message(callback, bot)
    else:
        await callback.answer("Вы еще не подписались на канал 😢. Пожалуйста, подпишитесь!", show_alert=True)
