import os
from html import escape
from datetime import timedelta
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, InputMediaPhoto
from aiogram.enums import ParseMode
from config.config import ADMINS, ADMIN_CHAT

import handlers.gold as g
import handlers.match_app as ma

from config.db_utils import get_db
from sqlalchemy import select
from models.User import User
from models.MarketListing import MarketListing

# Барахолка из Mini App: объявления игроков и их модерация админом в чате

router = Router()

MARKET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img', 'market')  # Фото объявлений

CATEGORIES = ['Ракетки', 'Мячи', 'Обувь', 'Одежда', 'Аксессуары', 'Другое']
CONDITIONS = ['Новое', 'Б/у']
MAX_ACTIVE = 5         # Не больше 5 объявлений на проверке и в продаже у одного игрока
LIFETIME_DAYS = 30     # Объявление видно 30 дней, потом его можно продлить
MAX_PHOTOS = 3


def get_photos(listing):  # Список файлов фото
    photos = []
    for name in listing.photos.split(','):
        if name:
            photos.append(name)
    return photos


def get_admin_chats():  # Куда отправлять на модерацию: чат админов или каждому админу
    if ADMIN_CHAT:
        return [ADMIN_CHAT]
    return ADMINS


async def send_to_moderation(listing, user, bot):  # Новое объявление — админу на проверку
    text = f"🛒 <b>Новое объявление на барахолке</b> (ID: {listing.id_listing})\n\n<b>Продавец:</b> <a href='{escape(user.link or '')}'>{escape(user.name_user or '')}</a>\n<b>Товар:</b> {escape(listing.title)}\n<b>Цена:</b> {listing.price} бел.руб.\n<b>Категория:</b> {listing.category} · {listing.item_condition}"
    if listing.description:
        text += f"\n\n{escape(listing.description)}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отклонить', callback_data=f'mk_no:{listing.id_listing}'),
                                                      InlineKeyboardButton(text='✅ Опубликовать', callback_data=f'mk_ok:{listing.id_listing}')]])

    photos = get_photos(listing)

    for chat_id in get_admin_chats():
        try:
            # Сначала фото (одно или альбомом), потом текст с кнопками
            if len(photos) > 1:
                media = []
                for name in photos:
                    media.append(InputMediaPhoto(media=FSInputFile(os.path.join(MARKET_DIR, name))))
                await bot.send_media_group(chat_id=chat_id, media=media)
            else:
                await bot.send_photo(chat_id=chat_id, photo=FSInputFile(os.path.join(MARKET_DIR, photos[0])))
            await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML, link_preview_options=ma.options, reply_markup=keyboard)
        except Exception as e:
            print(f"⚠️ Не удалось отправить объявление на модерацию в чат {chat_id}: {e}")


# Кнопка админа "✅ Опубликовать"
@router.callback_query(F.data.startswith('mk_ok:'))
async def market_approve(callback: CallbackQuery, bot):
    listing_id = int(callback.data.split(':')[1])

    async with get_db() as session:  # Используем контекстный менеджер

        listing = (await session.scalars(select(MarketListing).where(MarketListing.id_listing == listing_id).with_for_update())).first()

        if listing == None or listing.status != 'moderation':
            await callback.answer('⚠️ Это объявление уже проверено', show_alert=True)
            await ma.remove_buttons(callback)
            return

        listing.status = 'active'
        listing.expires = g.now_moscow() + timedelta(days=LIFETIME_DAYS)
        seller_id = listing.tg_user_id
        title = listing.title

        await callback.answer('✅ Объявление опубликовано')
        await ma.remove_buttons(callback)

    await ma.notify(bot, seller_id, f"✅ <b>Ваше объявление «{escape(title)}» опубликовано на барахолке!</b>\n\nОно будет видно {LIFETIME_DAYS} дней — потом его можно продлить", ma.app_keyboard('Открыть барахолку 🛒', 'market'))


# Кнопка админа "❌ Отклонить"
@router.callback_query(F.data.startswith('mk_no:'))
async def market_reject(callback: CallbackQuery, bot):
    listing_id = int(callback.data.split(':')[1])

    async with get_db() as session:  # Используем контекстный менеджер

        listing = (await session.scalars(select(MarketListing).where(MarketListing.id_listing == listing_id).with_for_update())).first()

        if listing == None or listing.status != 'moderation':
            await callback.answer('⚠️ Это объявление уже проверено', show_alert=True)
            await ma.remove_buttons(callback)
            return

        listing.status = 'rejected'
        seller_id = listing.tg_user_id
        title = listing.title

        await callback.answer('Объявление отклонено')
        await ma.remove_buttons(callback)

    await ma.notify(bot, seller_id, f"😔 <b>Объявление «{escape(title)}» не прошло проверку</b>\n\nЕсли есть вопросы — напишите в поддержку 🙋‍♂️ @sup_MM")
