from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm_payment = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✅ Подтвердить оплату!', callback_data='handle_button_click_confirm_payment')]]) # InlineKeyboardButton(text = '❌ Оплата не получена', callback_data='confirm_error_payment')

# send_error_payment = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Отменить', callback_data='start_message'), # сделать
#                                                         InlineKeyboardButton(text = '❌ Оплата не получена', callback_data='send_error_payment')]
#                                                         ])

# send_success_payment = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Отменить', callback_data='start_message'), # сделать
#                                                             InlineKeyboardButton(text = '✅ Подтвердить отправку!', callback_data='handle_button_click_confirm_payment')]
#                                                             ])
