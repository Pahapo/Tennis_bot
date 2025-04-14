from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import handlers.btn_tournaments as bt

exit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]])

tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Выйти', callback_data='start_message'),
                                                    InlineKeyboardButton(text = 'Изменить данные', callback_data='register_tournament')]
                                                    ])

tournaments_data = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='edit_tournament')]])

tournament_table = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Открыть таблицу 📋', url='https://docs.google.com/spreadsheets/d/1DdcB2aINDvH23RnMaWHBp4hDKTKP-VYlk82fowtZBHc/edit?usp=drivesdk')],
                                                         [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                         ])
edit_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнирная таблица 📋', callback_data='tournament_table')],
                                                        [InlineKeyboardButton(text = 'Создать турнир 🎾', callback_data='register_tournament')],
                                                        [InlineKeyboardButton(text = 'Список турниров 📖', callback_data='tournament_lists')],
                                                        [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
                                                        [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                        ])

tournament_info = bt.create_tournaments_keyboard(bt.get_list_tournaments())

reglament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='tournament_info'),
                                                    InlineKeyboardButton(text = 'Согласиться', callback_data='reglament_confirm')]
                                                    ])

address_court = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Северная Америка - Кижеватова 3Б', callback_data='court_1')],
                                                    [InlineKeyboardButton(text = 'Африка - Теслы 6', callback_data='court_2')],
                                                    [InlineKeyboardButton(text = 'Центральная Европа - Теслы 16', callback_data='court_3')],
                                                    [InlineKeyboardButton(text = 'Средиземноморский - Теслы 24', callback_data='court_4')],
                                                    [InlineKeyboardButton(text = 'Тропические острова - Лученка 24', callback_data='court_5')]
                                                    ])

level_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Золотой', callback_data='lvl_t_1')],
                                                        [InlineKeyboardButton(text = 'Серебряный', callback_data='lvl_t_2')],
                                                        [InlineKeyboardButton(text = 'Бронзовый', callback_data='lvl_t_3')],
                                                        [InlineKeyboardButton(text = 'Медный', callback_data='lvl_t_4')],
                                                        [InlineKeyboardButton(text = 'Железный', callback_data='lvl_t_5')],
                                                        [InlineKeyboardButton(text = 'Все дивизионы', callback_data='lvl_t_all')]
                                                        ])

reg_tournament_lvl = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Золотой 🥇', callback_data='lvl_p_1')],
                                                            [InlineKeyboardButton(text = 'Серебряный 🥈', callback_data='lvl_p_2')],
                                                            [InlineKeyboardButton(text = 'Бронзовый 🥉', callback_data='lvl_p_3')],
                                                            [InlineKeyboardButton(text = 'Медный 🎾', callback_data='lvl_p_4')],
                                                            [InlineKeyboardButton(text = 'Железный 🏃‍♂️', callback_data='lvl_p_5')],
                                                            [InlineKeyboardButton(text = 'Не знаю свой дивизион', callback_data='lvl_p_6')]
                                                            ])

reg_tournament_time1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Да', callback_data='time1_yes')],
                                                            [InlineKeyboardButton(text = 'Нет', callback_data='time1_no')]
                                                            ])

reg_tournament_time2 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Да', callback_data='time2_yes')],
                                                            [InlineKeyboardButton(text = 'Нет', callback_data='time2_no')]
                                                            ])