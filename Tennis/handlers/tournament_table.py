from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from config.config import EDITOR

import handlers.btn_tournaments as bt
import handlers.functions as f
import keywords.kw_tournament as kb


router = Router()


@router.callback_query(F.data == 'tournament_table')
async def tournament_table(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    user_id = callback.from_user.id

    if await f.check_subscription(callback.from_user.id, bot):
        if user_id in EDITOR:
            await callback.message.answer("<b>Турнирная таблица доступна для редактирования только организаторам турнира!</b>\n• Игроки имеют доступ \"читателя\"\n\n⚡️ Таблица создаётся автоматически после создания турнира редактором\n⚡️ Разные дивизионы расположены на разных листах", parse_mode=ParseMode.HTML, reply_markup=kb.table_list_edit)
        else:
            await callback.message.answer("<b>Турнирная таблица доступна для редактирования только организаторам турнира!</b>\n• Игроки имеют доступ \"читателя\"\n\n⚡️ Таблица создаётся автоматически после создания турнира редактором\n⚡️ Разные дивизионы расположены на разных листах", parse_mode=ParseMode.HTML, reply_markup=kb.table_list)
    else:
        await f.check_subscription_message(callback)



@router.callback_query(F.data == 'active_tournament_table')
async def active_tournament_table(callback: CallbackQuery, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):

        links = bt.get_links_tournaments()

        if not links:
            await callback.message.answer(f'<b>Пусто</b> 🥲\n\nНам жаль, но в данный момент нет ни одного активного турнира...\n\n<b>Хотите создать?</b>', parse_mode=ParseMode.HTML, reply_markup=kb.create_exit)
        else:
            active_tournament_table = bt.create_links_tournaments_keyboard(links)
            await callback.message.answer("<b>Тут отображается список активных турниров и те, которые закончились менее 3 дней назад</b> 👇", parse_mode=ParseMode.HTML, reply_markup=active_tournament_table)
    else:
        await f.check_subscription_message(callback)



@router.callback_query(F.data == 'history_tournament_table')
async def history_tournament_table(callback: CallbackQuery, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):

        links = bt.get_history_links_tournaments()

        if not links:
            await callback.message.answer(f'<b>Пусто</b> 🥲\n\nНам жаль, но завершённых турниров нет...', parse_mode=ParseMode.HTML, reply_markup=kb.table_list_back)
        else:
            history_tournament_table = bt.create_links_tournaments_keyboard(links)
            await callback.message.answer("<b>Тут отображается список турниров, попавших в архив</b> 👇", parse_mode=ParseMode.HTML, reply_markup=history_tournament_table)
    else:
        await f.check_subscription_message(callback)