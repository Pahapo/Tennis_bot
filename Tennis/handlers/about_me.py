from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram import F, Router

import keywords.kw_any as kb
import handlers.classes as cl


router = Router()


@router.callback_query(F.data == 'about_me')
async def about_me(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')

    # Создаём объект PlayerData
    player_data = cl.PlayerDataAbout(
        id = callback.from_user.id
    )

    await callback.message.answer((await player_data.about_player()), parse_mode=ParseMode.HTML, reply_markup=kb.exit)