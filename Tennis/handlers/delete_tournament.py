from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from aiogram import F, Router
from config.config import EDITOR

import keywords.kw_any as kb
import keywords.kw_tournament as kt
import handlers.btn_tournaments as bt
import handlers.functions as f

from config.db import session
from models.Tournament import Tournament


router = Router()


@router.callback_query(F.data == 'delete_tournament')
async def delete_tournament(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    tournament_info_delete = bt.create_tournaments_delete_keyboard(bt.get_list_tournaments_delete())

    await callback.message.answer('<b>Тут вы можете удалить турнир!</b>\nВыбери нужный турнир 👇', parse_mode=ParseMode.HTML, reply_markup=tournament_info_delete)


@router.callback_query(F.data.startswith("tournament_delete_"))
async def handle_level_buttons(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')   

    selected_tournament = callback.data.replace("tournament_delete_", "").replace("_delete", "")  # Получаем название выбранного турнира
    await state.update_data(name_tournament_delete = selected_tournament)

    await callback.message.answer(f'Подтвердите удаление турнира {selected_tournament}', parse_mode=ParseMode.HTML, reply_markup=kt.confirm_delete_tournament)
    

@router.callback_query(F.data == 'delete_tournament_anyway')
async def delete_tournament_anyway(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    user_id = callback.from_user.id
    if user_id in EDITOR:

        data = await state.get_data()
        name_tournament_delete = data.get("name_tournament_delete")

        selected_tournament = session.query(Tournament).filter(Tournament.name_tournament == name_tournament_delete).first()

        if selected_tournament:
            try:
                session.delete(selected_tournament)  # Удаляем объект из базы
                session.commit()
                print(f"Турнир '{name_tournament_delete}' был удалён редактором!")
                await callback.message.answer(f"✅ Турнир '{name_tournament_delete}' успешно удалён!", reply_markup=kb.exit)
            except Exception as e:
                session.rollback()
                await message.answer("<b>Произошла критическая ошибка!</b>\n\nОбратитесь в поддержку 🙋‍♂️ @mm_sup, мы устраним её!", parse_mode=ParseMode.HTML, reply_markup=kb.exit)
                raise e

        else:
            await callback.message.answer(f"Что-то пошло не так! Турнир '{name_tournament_delete}' не был найден\n\nХочешь узнать больше об ошибке? Обратись в поддержку\n🙋‍♂️ Поддержка @sup_MM", reply_markup=kb.exit)
    else:
        await callback.message.answer('Функция недоступна! Вы не редактор! ❌')
        await f.start_message(callback, bot)