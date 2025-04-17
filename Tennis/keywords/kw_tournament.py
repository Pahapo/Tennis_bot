from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import handlers.btn_tournaments as bt

exit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]])

tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Выйти', callback_data='start_message'),
                                                    InlineKeyboardButton(text = 'Изменить данные', callback_data='create_tournament')]
                                                    ])

tournaments_data = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Удалить участника 🚫', callback_data='delete_players')],
                                                        [InlineKeyboardButton(text = 'Назад', callback_data='edit_tournament')]
                                                        ])

table_list = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнирные таблицы 📋', callback_data='active_tournament_table')], # исправить
                                                    [InlineKeyboardButton(text = 'Архив 📚', callback_data='history_tournament_table')], # исправить
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                    ])

create_exit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Создать турнир 🎾', callback_data='create_tournament')], # исправить
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='tournament_table')]
                                                    ])

# Вывод кнопок турнира
tournament_info = bt.create_tournaments_keyboard(bt.get_list_tournaments())

# Вывод кнопок под ссылку турнира
active_tournament_table = bt.create_links_tournaments_keyboard(bt.get_links_tournaments())

# Вывод кнопок под ссылку турнира, которые попали в архив
history_tournament_table = bt.create_links_tournaments_keyboard(bt.get_history_links_tournaments())

# Вывод кнопок под ссылку турнира для удаления игрока
tournament_info_del_players = bt.create_tournaments_keyboard_players(bt.get_list_tournaments_players())

# Вывод кнопок для редактирования турнира
tournament_info_edit = bt.create_tournaments_edit_keyboard(bt.get_list_tournaments_edit())

# Вывод кнопок для удаления турнира
tournament_info_delete = bt.create_tournaments_delete_keyboard(bt.get_list_tournaments_delete())

confirm_delete_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='edit_tournament'),
                                                                InlineKeyboardButton(text = '✅ Подтвердить!', callback_data='delete_tournament_anyway')]
                                                                ])

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

add_level_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Добавить дивизион ⚡️', callback_data='add_level_tournament')],
                                                            [InlineKeyboardButton(text = 'Нет', callback_data='not_add_level_tournament')]
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