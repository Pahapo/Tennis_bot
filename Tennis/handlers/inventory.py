import os
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.enums import ParseMode
from aiogram import F, Router

import keywords.kw_any as ka
import handlers.functions as f
import handlers.classes as cl

from config.db import session
from models.Inventory import Inventory

router = Router()


@router.callback_query(F.data == 'inventory')
async def inventory(callback: CallbackQuery, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        if os.path.exists("Tennis/img/inventory/inventory.jpg"):  # Проверка, есть ли файл
            photo = FSInputFile("Tennis/img/inventory/inventory.jpg")  # Загружаем файл
            await callback.message.answer_photo(photo, caption=f"<b>На барахолке ты найдёшь инвентарь, который выставили игроки 🛒 Хочешь продать? 🤔\nСоздай своё объявление!</b>\n\n🎾 <b>Хорошие новости</b>, ты можешь приобрести инвентарь для тенниса прямо в боте!\n\n🤖 <b>Что я могу предложить?</b>\n• Теннисные мячи (Babolat, Head)\n• Виброгасители (Wilson)\n• Намотки (Wilson, Tecnifibre)", parse_mode=ParseMode.HTML, reply_markup=ka.inventory)
        else:
            await callback.message.answer(f"<b>На барахолке ты найдёшь инвентарь, который выставили игроки 🛒 Хочешь продать? 🤔\nСоздай своё объявление!</b>\n\n🎾 <b>Хорошие новости</b>, ты можешь приобрести инвентарь для тенниса прямо в боте!\n\n🤖 <b>Что я могу предложить?</b>\n• Теннисные мячи (Babolat, Head)\n• Виброгасители (Wilson)\n• Намотки (Wilson, Tecnifibre)", parse_mode=ParseMode.HTML, reply_markup=ka.inventory)
    else:
        await f.check_subscription_message(callback)


# Отправка сообщения inventory


# @router.callback_query(F.data == 'adm')
# async def register(callback: CallbackQuery, state:FSMContext):
#     await callback.answer('')
#     await state.set_state(cl.SendMessage.invent)
#     await callback.message.answer('Введи сообщение, которое хочешь разослать (только текст) 👇')

# @router.message(cl.SendMessage.invent)
# async def sending_messages(message: Message, state:FSMContext):   
# 
#     await state.set_state(None) 

#     check = Inventory(photo = 'img', description = message.html_text)
#     session.add(check)
#     session.commit()



@router.callback_query(F.data == 'get_inventory1')
async def register_inventory(callback: CallbackQuery):
    await callback.answer('')
    list_inventory = session.query(Inventory).filter(Inventory.photo.like("%1.%")).all()

    if os.path.exists("Tennis/img/inventory/1.jpg"):
        photo_header = FSInputFile("Tennis/img/inventory/1.jpg")
        await callback.message.answer_photo(photo_header)

    for inventory in list_inventory:
        if os.path.exists(f"Tennis/img/inventory/{inventory.photo}.jpg"):
            pyth_photo = f"Tennis/img/inventory/{inventory.photo}.jpg"
            photo = FSInputFile(pyth_photo)
            await callback.message.answer_photo(photo, caption=inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)
        else:
            await callback.message.answer(inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)


@router.callback_query(F.data == 'get_inventory2')
async def register_inventory(callback: CallbackQuery):
    await callback.answer('')
    list_inventory = session.query(Inventory).filter(Inventory.photo.like("%2.%")).all()

    if os.path.exists("Tennis/img/inventory/2.jpg"):
        photo_header = FSInputFile("Tennis/img/inventory/2.jpg")
        await callback.message.answer_photo(photo_header)

    for inventory in list_inventory:
        if os.path.exists(f"Tennis/img/inventory/{inventory.photo}.jpg"):
            pyth_photo = f"Tennis/img/inventory/{inventory.photo}.jpg"
            photo = FSInputFile(pyth_photo)
            await callback.message.answer_photo(photo, caption=inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)
        else:
            await callback.message.answer(inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)


@router.callback_query(F.data == 'get_inventory3')
async def register_inventory(callback: CallbackQuery):
    await callback.answer('')
    list_inventory = session.query(Inventory).filter(Inventory.photo.like("%3.%")).all()

    if os.path.exists("Tennis/img/inventory/3.jpg"):
        photo_header = FSInputFile("Tennis/img/inventory/3.jpg")
        await callback.message.answer_photo(photo_header)

    for inventory in list_inventory:
        if os.path.exists(f"Tennis/img/inventory/{inventory.photo}.jpg"):
            pyth_photo = f"Tennis/img/inventory/{inventory.photo}.jpg"
            photo = FSInputFile(pyth_photo)
            await callback.message.answer_photo(photo, caption=inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)
        else:
            await callback.message.answer(inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)