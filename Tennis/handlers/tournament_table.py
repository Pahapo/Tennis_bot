from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

import handlers.btn_tournaments as bt
import keywords.kw_tournament as kb
import handlers.functions as f

router = Router()

# ПРЕДУСМОТРЕТЬ, ЕСЛИ СПИСОК ПУСТОЙ, ТО ВЫВОДИТЬ ДРУГОЕ СООБЩЕНИЕ ! ! !


@router.callback_query(F.data == 'tournament_table')
async def tournament_table(callback: CallbackQuery, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        await callback.message.answer("<b>Турнирная таблица доступна для редактирования только организаторам турнира!</b>\n• Игроки имеют доступ \"читателя\"\n\n⚡️ Таблица создаётся автоматически после создания турнира редактором\n⚡️ Разные дивизионы расположены на разных листах", parse_mode=ParseMode.HTML, reply_markup=kb.table_list)
    else:
        await f.check_subscription_message(callback)



@router.callback_query(F.data == 'active_tournament_table')
async def active_tournament_table(callback: CallbackQuery, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        if bt.get_links_tournaments() == {}:
            await callback.message.answer(f'<b>Пусто</b> 🥲\n\nНам жаль, но в данный момент нет ни одного активного турнира...\n\n<b>Хотите создать?</b>', parse_mode=ParseMode.HTML, reply_markup=kb.create_exit)
        else:
            await callback.message.answer("<b>Тут отображается список активных турниров и те, которые закончились менее 3 дней назад</b> 👇", parse_mode=ParseMode.HTML, reply_markup=kb.active_tournament_table)
    else:
        await f.check_subscription_message(callback)



@router.callback_query(F.data == 'history_tournament_table')
async def history_tournament_table(callback: CallbackQuery, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        if bt.get_history_links_tournaments() == {}:
            await callback.message.answer(f'<b>Пусто</b> 🥲\n\nНам жаль, но завершённых турниров нет...', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
        else:
            await callback.message.answer("<b>Тут отображается список турниров, попавших в архив</b> 👇", parse_mode=ParseMode.HTML, reply_markup=kb.history_tournament_table)
    else:
        await f.check_subscription_message(callback)