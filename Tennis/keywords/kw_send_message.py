from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

send_message_war = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='start_message'),
                                                        InlineKeyboardButton(text = '✅ Сделать рассылку!', callback_data='send_war')]
                                                        ])

send_message = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='start_message'),
                                                    InlineKeyboardButton(text = '✅ Подтвердить отправку!', callback_data='send')]
                                                    ])