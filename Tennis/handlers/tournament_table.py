from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

import keywords.kw_tournament as kb
import handlers.functions as f

router = Router()


@router.callback_query(F.data == 'tournament_table')
async def tournament_table(callback: CallbackQuery, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        await callback.message.answer("⚠️ Перед выставлением счёта в таблице, пожалуйста, ознакомьтесь с <b>\"Инструкцией заполнения столбца (счёт)\"</b>, расположенной в <b>ячейке U1</b>", parse_mode=ParseMode.HTML, reply_markup=kb.tournament_table)
    else:
        await f.check_subscription_message(callback)