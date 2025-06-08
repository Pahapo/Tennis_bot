from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router

from config.config import BOT_USERNAME



router = Router()

# Вывод кнопок под реферальную систему

def generate_share_referral_link(user_id, invite_text):
    buttons = [
        [InlineKeyboardButton(text="Отправить другу 🙋‍♂️", url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME}?start=ref_{user_id}&text={invite_text}")]
    ]
    buttons.append([InlineKeyboardButton(text='Главное меню!', callback_data='start_message')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)