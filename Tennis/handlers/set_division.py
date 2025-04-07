import json
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram import F, Router
from config import MAIN_EDITOR

import handlers.keywords as kb
import handlers.classes as cl
import handlers.start as st



router = Router()


@router.callback_query(F.data == 'set_division')
async def set_division(callback: CallbackQuery, state:FSMContext):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    await callback.message.answer('<b>Тут вы можете установить/изменить рейтинг игрокам</b>\nВыберите нужный вариант 👇', parse_mode=ParseMode.HTML, reply_markup=kb.set_division)


@router.callback_query(F.data == 'find_users')
async def find_users(callback: CallbackQuery, state:FSMContext):
    await callback.answer('') # нужно отвечать чисто callback, иначе выбранная кнопка продолжить мигать
    await state.set_state(cl.FindUser.name)
    
    user_id = callback.from_user.id
    if user_id in MAIN_EDITOR:
        await callback.message.answer('Введите <b>username</b> игрока 👇', parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer('Функция недоступна! Вы не главный редактор! 🚫')
        st.cmd_start()



@router.message(cl.FindUser.name)
async def find_name(message: Message, state:FSMContext):
    data = await state.get_data()
    name_finder_user = data.get("name")

    if '@' in name_finder_user:
        name_finder_user = name_finder_user.replace('@', '', 1)


    # ПРОДОЛЖИТЬ ПИСАТЬ ПОИСК ИГРОКОВ !!!





    user_id = callback.from_user.id
    if user_id in MAIN_EDITOR:
        pass