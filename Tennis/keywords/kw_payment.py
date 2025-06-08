from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm_payment = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '❌ Оплата не получена', callback_data='confirm_error_payment')],
                                                        [InlineKeyboardButton(text = '✅ Подтвердить оплату!', callback_data='handle_button_click_confirm_payment')]
                                                        ])

confirm_payment_pl = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '❌ Отменить и выйти', callback_data='start_message')]])

payment_with_coins = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Продолжить оплату 💳', callback_data='reglament_confirm')],
                                                            [InlineKeyboardButton(text = '❌ Отменить и выйти', callback_data='start_message')]
                                                            ])