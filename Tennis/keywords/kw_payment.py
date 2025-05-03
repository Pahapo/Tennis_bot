from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm_payment = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '❌ Оплата не получена', callback_data='confirm_error_payment')],
                                                        [InlineKeyboardButton(text = '✅ Подтвердить оплату!', callback_data='handle_button_click_confirm_payment')]
                                                        ])