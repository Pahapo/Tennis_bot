from aiogram.types import CallbackQuery, InputFile, LinkPreviewOptions, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import F, Router
import os

import keywords.kw_any as ka
import handlers.classes as cl
import handlers.functions as f

from config.db import session
from models.Inventory import Inventory

router = Router()


@router.callback_query(F.data == 'inventory')
async def inventory(callback: CallbackQuery, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        if os.path.exists("img/inventory.jpg"):  # Проверка, есть ли файл
            photo = InputFile("img/inventory.jpg")  # Загружаем файл
            await callback.message.answer_photo(photo, caption=f"<b>На барахолке ты найдёшь инвентарь, который выставили игроки 🛒 Хочешь продать? 🤔\nСоздай своё объявление!</b>\n\n🎾 <b>Хорошие новости</b>, ты можешь приобрести инвентарь для тенниса прямо в боте!\n\n🤖 <b>Что я могу предложить?</b>\n• Теннисные мячи (Babolat, Head)\n• Виброгасители (Wilson)\n• Намотки (Wilson, Tecnifibre)", parse_mode=ParseMode.HTML, reply_markup=ka.inventory)
        else:
            await callback.message.answer(f"<b>На барахолке ты найдёшь инвентарь, который выставили игроки 🛒 Хочешь продать? 🤔\nСоздай своё объявление!</b>\n\n🎾 <b>Хорошие новости</b>, ты можешь приобрести инвентарь для тенниса прямо в боте!\n\n🤖 <b>Что я могу предложить?</b>\n• Теннисные мячи (Babolat, Head)\n• Виброгасители (Wilson)\n• Намотки (Wilson, Tecnifibre)", parse_mode=ParseMode.HTML, reply_markup=ka.inventory)
    else:
        await f.check_subscription_message(callback)


@router.callback_query(F.data == 'get_inventory1')
async def register_inventory(callback: CallbackQuery):
    await callback.answer('')
    list_inventory = session.query(Inventory).filter(Inventory.photo.like("%1.%")).all()

    if os.path.exists("img/1.jpg"):
        photo_header = InputFile("img/1.jpg")
        await callback.message.answer_photo(photo_header)

    for inventory in list_inventory:
        if os.path.exists(f"img/{inventory.photo}.jpg"):
            pyth_photo = f"img/{inventory.photo}.jpg"
            photo = InputFile(pyth_photo)
            await callback.message.answer_photo(photo, caption=inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)
        else:
            await callback.message.answer(inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)


@router.callback_query(F.data == 'get_inventory2')
async def register_inventory(callback: CallbackQuery):
    await callback.answer('')
    list_inventory = session.query(Inventory).filter(Inventory.photo.like("%2.%")).all()

    if os.path.exists("img/2.jpg"):
        photo_header = InputFile("img/2.jpg")
        await callback.message.answer_photo(photo_header)

    for inventory in list_inventory:
        if os.path.exists(f"img/{inventory.photo}.jpg"):
            pyth_photo = f"img/{inventory.photo}.jpg"
            photo = InputFile(pyth_photo)
            await callback.message.answer_photo(photo, caption=inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)
        else:
            await callback.message.answer(inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)


@router.callback_query(F.data == 'get_inventory3')
async def register_inventory(callback: CallbackQuery):
    await callback.answer('')
    list_inventory = session.query(Inventory).filter(Inventory.photo.like("%3.%")).all()

    if os.path.exists("img/3.jpg"):
        photo_header = InputFile("img/3.jpg")
        await callback.message.answer_photo(photo_header)

    for inventory in list_inventory:
        if os.path.exists(f"img/{inventory.photo}.jpg"):
            pyth_photo = f"img/{inventory.photo}.jpg"
            photo = InputFile(pyth_photo)
            await callback.message.answer_photo(photo, caption=inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)
        else:
            await callback.message.answer(inventory.description, parse_mode=ParseMode.HTML, reply_markup=ka.inventory_exit)