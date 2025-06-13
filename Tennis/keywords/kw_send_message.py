from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

send_message_war = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✅ Сделать рассылку!', callback_data='send_war')],
                                                        [InlineKeyboardButton(text = 'Добавить callback', callback_data='add_btn_callback'),
                                                         InlineKeyboardButton(text = 'Добавить link', callback_data='add_btn_link')],
                                                        [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                        ])

send_message = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✅ Подтвердить отправку!', callback_data='send')],
                                                    [InlineKeyboardButton(text = 'Исправить сообщение', callback_data='sending_messages')],
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                    ])

send_message_photo_q = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Текст', callback_data='sending_messages_text'),
                                                    InlineKeyboardButton(text = 'Текст с фото', callback_data='sending_messages_photo')],
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                    ])