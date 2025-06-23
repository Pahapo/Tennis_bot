from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LinkPreviewOptions
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ParseMode
from config.config import ADMINS, MAIN_EDITOR, EDITOR, DIVISION_EDITOR

import keywords.kw_tournament as kb
import keywords.kw_any as ka
import handlers.functions as f

from config.db import session
from models.User import User
from models.Division import Division


router = Router()

@router.callback_query(F.data == 'player_without_division')
async def player_without_division(callback: CallbackQuery, state: FSMContext, bot):
    await callback.answer('')

    data = await state.get_data()
    count = data.get("next_user")

    options = LinkPreviewOptions(
        is_disabled=True
    )

    user_id = callback.from_user.id
    if user_id in ADMINS or user_id in MAIN_EDITOR or user_id in EDITOR or str(user_id) == DIVISION_EDITOR:
                        
        users_without_division = session.query(User).filter(User.division_level == None).all()
        count_users = len(users_without_division)

        await callback.answer(f'Всего игроков без дивизиона {count_users} чел.')

        try:
            if users_without_division:
                if len(users_without_division) > count:
                    user = users_without_division[count]
                    await state.update_data(pl_id_without_div = user.tg_user_id)

                    if len(users_without_division) == count + 1:
                        await callback.message.edit_text(f'<b>Игрок 🙋‍♂️ {user.name_user} ожидает выбора дивизиона</b>\n\nСсылка: {user.link}\nОписание уровня игры: {user.skill}', parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=ka.pl_without_div_end)
                    else:
                        await callback.message.edit_text(f'<b>Игрок 🙋‍♂️ {user.name_user} ожидает выбора дивизиона</b>\n\nСсылка: {user.link}\nОписание уровня игры: {user.skill}', parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=ka.pl_without_div)
                else:
                    await callback.message.edit_text(f'<b>Все игроки теперь имеют дивизион!</b>\nОтличная работа! 👍🏻', parse_mode=ParseMode.HTML, reply_markup=ka.exit)
            else:
                await callback.message.edit_text(f'<b>Все игроки теперь имеют дивизион!</b>\nОтличная работа! 👍🏻', parse_mode=ParseMode.HTML, reply_markup=ka.exit)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                print("Сообщение не изменилось, пропускаем...")
            else:
                raise  # Перебрасываем другие ошибки
    else:
        await callback.message.answer('Функция недоступна! Вы не главный редактор / редактор! ❌')
        await f.start_message(callback, bot)



@router.callback_query(F.data.in_(["lvl_wd_1", "lvl_wd_2", "lvl_wd_3", "lvl_wd_4", "lvl_wd_5"]))
async def handle_level_buttons(call: CallbackQuery, state: FSMContext, bot):

    level = ''
    
    data = await state.get_data()
    user_id = data.get("pl_id_without_div")

    if call.data == "lvl_wd_1":
        level = '1'
    elif call.data == "lvl_wd_2":
        level = '2'
    elif call.data == "lvl_wd_3":
        level = '3'
    elif call.data == "lvl_wd_4":
        level = '4'
    elif call.data == "lvl_wd_5":
        level = '5'

    user = session.query(User).filter(User.tg_user_id == user_id).first()
    try:
        user.division_level = level
        session.commit()

        print(f"Установлен дивизион для пользователя \"{user.name_user}\"!")
        await call.answer(f"Дивизион установлен! ✅", show_alert=False)

        name_division = session.query(Division).filter(Division.division_id == int(level)).first()
        division_lvl = name_division.name_division
    
        message_text_send = f"<b>Дорогой {user.name_user}, сообщаем Вам о том, что Вам установлен дивизион!</b> 🏆\n\nДивизион: <b>{division_lvl}</b>\n\n<b>Поздравляем!</b> 🎉 Теперь вы можете принять участие в турнирах!"
    except Exception as e:
        session.rollback()
        raise e

    try:
        await bot.send_message(chat_id=user.tg_user_id, text=message_text_send, parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    except Exception as e:
        print(f"❌ Не удалось отправить сообщение об установлении дивизиона пользователю с id: {user.tg_user_id} из-за ошибки: {e}")


    await player_without_division(call, state)


@router.callback_query(F.data == 'player_without_division_next')
async def player_without_division_next(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    
    data = await state.get_data()
    count = data.get("next_user")
    count += 1
    await state.update_data(next_user = count)

    await player_without_division(callback, state)