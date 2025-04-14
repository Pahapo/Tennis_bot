from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

player = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='contestant'),
                                                InlineKeyboardButton(text = 'Изменить данные', callback_data='register_player')]
                                                ])

players = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Выбрать соперника 🙋‍♂️', callback_data='search_contestant')],
                                                [InlineKeyboardButton(text = 'Моя карточка 📋', callback_data='get_data_player')],
                                                [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                ])

players_data = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='contestant')]])

sex = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Мужчина', callback_data='men')],
                                            [InlineKeyboardButton(text = 'Женщина', callback_data='women')]
                                            ])

create_card = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='contestant'),
                                                    InlineKeyboardButton(text = 'Создать 📋', callback_data='register_player')]
                                                    ])

user_lvl = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Золотой 🥇', callback_data='lvl_u_1')],
                                                [InlineKeyboardButton(text = 'Серебряный 🥈', callback_data='lvl_u_2')],
                                                [InlineKeyboardButton(text = 'Бронзовый 🥉', callback_data='lvl_u_3')],
                                                [InlineKeyboardButton(text = 'Медный 🎾', callback_data='lvl_u_4')],
                                                [InlineKeyboardButton(text = 'Железный 🏃‍♂️', callback_data='lvl_u_5')]
                                                ])