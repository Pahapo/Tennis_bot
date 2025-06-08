from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

exit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]])

player = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='match'),
                                                InlineKeyboardButton(text = 'Изменить данные', callback_data='register_player')]
                                                ])

player_get_card = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='match'),
                                                InlineKeyboardButton(text = 'Изменить данные', callback_data='register_player')],
                                                [InlineKeyboardButton(text = '❌ Удалить', callback_data='delete_match')]
                                                ])

players = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Найти соперника 🙋‍♂️', callback_data='search_match')],
                                                [InlineKeyboardButton(text = 'Создать запрос / Мои запросы 📋', callback_data='match_requests')],
                                                [InlineKeyboardButton(text = 'Мои подтверждённые игры 🎾', callback_data='my_match')],
                                                [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                ])

confirm_match = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Мои подтверждённые игры 🎾', callback_data='my_match')],
                                                [InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]
                                                ])

players_data = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='match'),
                                                    InlineKeyboardButton(text = '✅ Подать заявку', callback_data='apply_match')]
                                                    ]) 

matches_not_found = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='match'),
                                                    InlineKeyboardButton(text = 'Создать 📋', callback_data='register_player')]
                                                    ]) 

my_matches = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='match'),
                                                    InlineKeyboardButton(text = 'Найти соперника 🙋‍♂️', callback_data='search_match')]
                                                    ]) 

apply_match = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '❌ Отклонить', callback_data='reject_match'),
                                                    InlineKeyboardButton(text = '✅ Принять', callback_data='accept_match')]
                                                    ]) 

sex = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Мужчина', callback_data='men')],
                                            [InlineKeyboardButton(text = 'Женщина', callback_data='women')]
                                            ])

create_card = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='match'),
                                                    InlineKeyboardButton(text = 'Создать 📋', callback_data='register_player')]
                                                    ])

user_lvl = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Золотой 🥇', callback_data='lvl_u_1')],
                                                [InlineKeyboardButton(text = 'Серебряный 🥈', callback_data='lvl_u_2')],
                                                [InlineKeyboardButton(text = 'Бронзовый 🥉', callback_data='lvl_u_3')],
                                                [InlineKeyboardButton(text = 'Медный 🎾', callback_data='lvl_u_4')],
                                                [InlineKeyboardButton(text = 'Железный 🏃‍♂️', callback_data='lvl_u_5')]
                                                ])

booking_court_q = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Да', callback_data='yes_b_c')],
                                                        [InlineKeyboardButton(text = 'Нет', callback_data='no_b_c')]
                                                        ])

comment_q = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Да', callback_data='yes_c')],
                                                        [InlineKeyboardButton(text = 'Нет', callback_data='no_c')]
                                                        ])

add_card_q = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='match'),
                                                    InlineKeyboardButton(text = 'Создать 📋', callback_data='register_player')]
                                                    ])
