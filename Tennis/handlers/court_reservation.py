from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

import handlers.keywords as kb
import handlers.functions as f

router = Router()


@router.callback_query(F.data == 'court_reservation')
async def contestant(callback: CallbackQuery, bot):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать

    if await f.check_subscription(callback.from_user.id, bot):
        await callback.message.answer("Для бронирования корта перейдите по кнопке ниже 👇\n\nВведите желаемую дату и время игры", parse_mode=ParseMode.HTML, reply_markup=kb.court_reservation)
    else:
        await f.check_subscription_message(callback)
