from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

import keywords.kw_any as kb
import handlers.functions as f


router = Router()


@router.callback_query(F.data == 'court_reservation')
async def match(callback: CallbackQuery, state: FSMContext, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        user_id = callback.from_user.id

        if await f.check_fast_user(user_id):
            await callback.message.answer("\"<b>Быстрое бронирование 🎾</b>\"\n• Бронь любого корта на месяц вперёд\n• Автоматическое бронирования выбранного времени\n• До 5 броней в неделю\n\n\"<b>Обычное бронирование</b>\"\n• Бронь любого корта на 5 дней вперёд\n• Бронирование зависит от вашей скорости\n• До 2 броней в неделю\n\n⚠️ Во время открытия бронирования люди часто ставят отложенные сообщения или ждут начала, чтобы в ручном режиме успеть забронировать. Часто даже отложенные сообщения не спасают, и уже через 10 минут всё вечернее время занято.\n\n<b>Не хотите рисковать? Используйте \"Быстрое бронирование🎾\"!</b>", parse_mode=ParseMode.HTML, reply_markup=kb.court_reservation_fast)
        else:
            await callback.message.answer("<b>Бронирование кортов через бота</b> 🎾\n\n• Бронь любого корта на 5 дней вперёд\n• Бронирование зависит от вашей скорости\n• До 2 броней в неделю", parse_mode=ParseMode.HTML, reply_markup=kb.court_reservation)
    else:
        await f.check_subscription_message(callback)
