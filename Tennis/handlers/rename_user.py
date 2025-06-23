from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.enums import ParseMode
from aiogram import F, Router
from config.config import EDITOR

import keywords.kw_any as kb
import handlers.classes as cl
import handlers.functions as f
import handlers.validation as valid

from config.db import session
from models.Division import Division
from models.User import User


router = Router()


@router.callback_query(F.data == 'rename_user')
async def rename_user(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await callback.message.answer('<b>Тут вы можете изменить имя игрокам</b>\n\nНайдите игрока по поиску 🔍', parse_mode=ParseMode.HTML, reply_markup=kb.rename_user)


@router.callback_query(F.data == 'find_users_for_rename')
async def find_users_for_rename(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')
    await state.set_state(cl.FindUser.name_rename)
    
    user_id = callback.from_user.id
    if user_id in EDITOR:
        await callback.message.answer('Введите <b>username</b> игрока 👇', parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer('Функция недоступна! Вы не главный редактор / редактор! ❌')
        await f.start_message(callback, bot)


@router.message(cl.FindUser.name_rename)
async def find_rename(message: Message, state:FSMContext):
    await state.update_data(name = message.text)
    name_finder_user = message.text.lower()

    await state.set_state(None)
    
    if 'https://t.me/' not in name_finder_user:
        if '@' in name_finder_user:
            name_finder_user = name_finder_user.replace('@', '', 1)

        name_finder_user = 'https://t.me/' + name_finder_user

    options = LinkPreviewOptions(
        is_disabled=True
    )

    list_finder_user = [row[0] for row in session.query(User.link).all()]

    if name_finder_user in list_finder_user:
        user = session.query(User).filter_by(link = name_finder_user).first()
        await state.update_data(tg_user_id = user.tg_user_id)

        division_lvl = ''

        if user.division_level != None:
            name_division = session.query(Division).filter(Division.division_id == int(user.division_level)).first()
            division_lvl = name_division.name_division
        else:
            division_lvl = 'Не определён'

        await message.answer(f'<b>Найден пользователь {user.name_user} 🙋‍♂️</b>\n\nСсылка: {user.link}\nДивизион: {division_lvl}', parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.edit_rename)
    else:
        await message.answer('Пользователь с таким <b>username</b> не найден!', parse_mode=ParseMode.HTML, reply_markup=kb.back_rename)


@router.callback_query(F.data == 'set_new_name_user')
async def set_new_name_user(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await state.set_state(cl.FindUser.rename)
    await callback.message.answer('Введите новое имя для пользователя 👇')


@router.message(cl.FindUser.rename)
async def find_name_rename(message: Message, state:FSMContext):
    rename = message.text.strip()
    # Проверяем, корректно ли введен текст
    if not valid.validate_name(rename):
        remaining_chars = len(rename) - 64
        await message.answer(f"⚠ Ошибка! Длина ответа превышена на {remaining_chars} символов. Попробуйте снова 👇")
        return  # Останавливаем обработку, чтобы пользователь ввел данные снова
    
    await state.set_state(None)

    data = await state.get_data()
    name_finder_user = data.get("tg_user_id")

    user = session.query(User).filter_by(tg_user_id = name_finder_user).first()
    
    if user:
        try:
            old_name = user.name_user
            user.name_user = rename

            print(f'Пользователь "{old_name}" был переименован на {rename}!')
            await message.answer(f'✅ Пользователь "{old_name}" был переименован на {rename}!', reply_markup=kb.back_rename)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
    else:
        await message.answer(f'❌ Пользователь "{user.name_user}" не был переименован!', reply_markup=kb.back_rename)
        print(f"ОШИБКА! Пользователь '{user.name_user}' не был переименован!")  
    await state.clear()