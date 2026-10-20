from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.enums import ParseMode
from aiogram import F, Router
from config.config import MAIN_EDITOR, EDITOR

import keywords.kw_any as kb
import keywords.kw_start as ks
import keywords.kw_user as kb_user
import handlers.classes as cl
import handlers.functions as f

from config.db_utils import get_db_readonly, get_db
from sqlalchemy import select
from models.Division import Division
from models.User import User


router = Router()


@router.callback_query(F.data == 'main_edit_level_ban')
async def main_edit_level_ban(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await callback.message.answer('<b>Тут вы можете изменить дивизион игрокам, а так же забанить тех, кто нарушает регламент</b>\n\nВыберите нужный вариант 👇', parse_mode=ParseMode.HTML, reply_markup=ks.main_edit_level_ban)


@router.callback_query(F.data == 'set_division')
async def set_division(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await callback.message.answer('<b>Тут вы можете установить/изменить дивизион игрокам</b>\n\nВыберите нужный вариант 👇', parse_mode=ParseMode.HTML, reply_markup=kb.set_division)
    await state.update_data(next_user = 0)


@router.callback_query(F.data == 'find_users_for_division')
async def find_users_for_division(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')
    await state.set_state(cl.FindUser.name_division)
    
    user_id = callback.from_user.id
    if user_id in MAIN_EDITOR or user_id in EDITOR:
        await callback.message.answer('Введите <b>username</b> игрока 👇', parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer('Функция недоступна! Вы не главный редактор / редактор! ❌')
        await f.start_message(callback, bot)


@router.message(cl.FindUser.name_division)
async def find_name_division(message: Message, state:FSMContext):
    await state.update_data(name = message.text)
    name_finder_user = message.text.lower()

    async with get_db_readonly() as session:  # Используем контекстный менеджер

        await state.set_state(None)

        if 'https://t.me/' not in name_finder_user:
            if '@' in name_finder_user:
                name_finder_user = name_finder_user.replace('@', '', 1)

            name_finder_user = 'https://t.me/' + name_finder_user

        options = LinkPreviewOptions(
            is_disabled=True
        )

        list_finder_user = (await session.scalars(select(User.link))).all()

        if name_finder_user in list_finder_user:
            user = (await session.scalars(select(User).where(User.link == name_finder_user))).first()
            await state.update_data(tg_user_id = user.tg_user_id)

            if user.division_level != None:
                name_division = (await session.scalars(select(Division).where(Division.division_id == int(user.division_level)))).first()
                division_lvl = name_division.name_division
            else:
                division_lvl = 'Не определён'
            
            await message.answer(f'<b>Найден пользователь 🙋‍♂️ {user.name_user}</b>\n\nСсылка: {user.link}\nДивизион: {division_lvl} ⚡️ {user.rating}', parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.edit_division)
        else:
            await message.answer('Пользователь с таким <b>username</b> не найден!',parse_mode=ParseMode.HTML, reply_markup=kb.back_division)



@router.callback_query(F.data == 'set_new_division')
async def set_new_division(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await callback.message.answer('Выберите новый дивизион для игрока 👇', reply_markup=kb_user.user_lvl)


@router.callback_query(F.data.in_(["lvl_u_1", "lvl_u_2", "lvl_u_3", "lvl_u_4", "lvl_u_5"]))
async def handle_level_buttons(call: CallbackQuery, state: FSMContext, bot):
    await call.answer('')
    user_id = call.from_user.id

    async with get_db() as session:  # Используем контекстный менеджер

        level_user = ''
        
        if call.data == "lvl_u_1":
            level_user = 1
        elif call.data == "lvl_u_2":
            level_user = 2
        elif call.data == "lvl_u_3":
            level_user = 3
        elif call.data == "lvl_u_4":
            level_user = 4
        elif call.data == "lvl_u_5":
            level_user = 5

        data = await state.get_data()
        name_finder_user = data.get("tg_user_id")

        user = (await session.scalars(select(User).where(User.tg_user_id == name_finder_user))).first()

        if user:
            try:
                division_lvl = ''
                user.division_level = level_user
                user.rating = get_rating_by_division(level_user)

                if user.division_level != None:
                    name_division = (await session.scalars(select(Division).where(Division.division_id == int(user.division_level)))).first()
                    division_lvl = name_division.name_division
                else:
                    division_lvl = 'Не определён'

                print(f"Дивизион пользователя \"{user.tg_user_id}\" был изменён на {division_lvl}! Дивизион исправил организатор: {user_id}")
                await call.message.answer(f"✅ Дивизион пользователя \"{user.name_user}\" был изменён на {division_lvl}!", reply_markup=kb.back_division)

                message_text_send = f"<b>Дорогой игрок, сообщаем Вам о том, что Ваш дивизион изменён!</b> 🏆\n\nНовый дивизион: <b>{division_lvl}</b>\n\n<b>Поздравляем!</b> 🎉"

                await bot.send_message(chat_id=user.tg_user_id, text=message_text_send, parse_mode=ParseMode.HTML, reply_markup=kb.exit)
            except Exception as e:
                print(f"⚠️ Не удалось отправить сообщение о изменении дивизиона пользователю с id: {user.tg_user_id} из-за ошибки: {e}")
        else:
            await call.message.answer(f"❌ <b>Пользователь не был найден!</b> Ошибка на стороне сервера!", parse_mode=ParseMode.HTML, reply_markup=kb.exit) 
            print(f"ОШИБКА! Дивизион пользователя \"{user.tg_user_id}\" не был изменён. Пользователь не найден в БД!")  
    await state.clear()
    

def get_rating_by_division(level_user):
    if level_user == 1:
        return 5.5
    elif level_user == 2:
        return 4.5
    elif level_user == 3:
        return 3.5
    elif level_user == 4:
        return 2.5
    else:
        return 1.5