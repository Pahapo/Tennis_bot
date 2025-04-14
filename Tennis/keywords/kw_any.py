from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

exit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]])

set_division = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Игроки без рейтинга 🙋‍♂️', callback_data='lvl_p_1')], # сделать!
                                                    [InlineKeyboardButton(text = 'Поиск игрока 🔍', callback_data='find_users_for_division')],
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                    ])

back_division = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Найти другого игрока 🔍', callback_data='find_users_for_division')],
                                                    [InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]
                                                    ])

edit_division = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Изменить рейтинг 🙋‍♂️', callback_data='set_new_division')],
                                                    [InlineKeyboardButton(text = 'Найти другого игрока 🔍', callback_data='find_users_for_division')],
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='set_division')]
                                                    ])

set_ban = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Поиск игрока 🔍', callback_data='find_users_for_ban')],
                                                [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                ])

back_ban = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Найти другого игрока 🔍', callback_data='find_users_for_ban')],
                                                [InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]
                                                ])

edit_ban = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Забанить 🚫', callback_data='set_new_ban')],
                                                [InlineKeyboardButton(text = 'Назад', callback_data='set_ban')]
                                                ])

court_reservation = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Забронировать корт 🎾', url='https://t.me/mw_tennis_bot')],
                                                         [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                         ])
