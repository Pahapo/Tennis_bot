from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

exit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]])

# division

set_division = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Игроки без дивизиона 🙋‍♂️', callback_data='player_without_division')], # сделать!
                                                    [InlineKeyboardButton(text = 'Поиск игрока 🔍', callback_data='find_users_for_division')],
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                    ])

back_division = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Найти другого игрока 🔍', callback_data='find_users_for_division')],
                                                    [InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]
                                                    ])

edit_division = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Изменить дивизион 🙋‍♂️', callback_data='set_new_division')],
                                                    [InlineKeyboardButton(text = 'Найти другого игрока 🔍', callback_data='find_users_for_division')],
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='set_division')]
                                                    ])

pl_without_div = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Золотой', callback_data='lvl_wd_1')],
                                                        [InlineKeyboardButton(text = 'Серебряный', callback_data='lvl_wd_2')],
                                                        [InlineKeyboardButton(text = 'Бронзовый', callback_data='lvl_wd_3')],
                                                        [InlineKeyboardButton(text = 'Медный', callback_data='lvl_wd_4')],
                                                        [InlineKeyboardButton(text = 'Железный', callback_data='lvl_wd_5')],
                                                        [InlineKeyboardButton(text = 'Пропустить пользователя 👉', callback_data='player_without_division_next')], # сделать!
                                                        [InlineKeyboardButton(text = 'Выйти', callback_data='set_division')]
                                                        ])

# ban

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

# delete from tournament

back_delete_players = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Найти другого игрока 🔍', callback_data='delete_players')],
                                                            [InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]
                                                            ])

edit_delete_players = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Удалить из турнира 🚫', callback_data='delete_players_tournaments')], # сделать!
                                                            [InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]
                                                            ])
