from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import handlers.btn_tournaments as bt

exit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]])

tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Выйти', callback_data='start_message'),
                                                    InlineKeyboardButton(text = 'Изменить данные', callback_data='create_tournament')]
                                                    ])

tournaments_data = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Удалить участника ❌', callback_data='delete_players')],
                                                        [InlineKeyboardButton(text = 'Назад', callback_data='main_edit_tournament')]
                                                        ])

tournaments_data_edit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Удалить участника ❌', callback_data='delete_players')],
                                                              [InlineKeyboardButton(text = 'Назад', callback_data='edit_tournament')]
                                                              ])

table_list = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнирные таблицы 📋', callback_data='active_tournament_table')],
                                                    [InlineKeyboardButton(text = 'Архив 📚', callback_data='history_tournament_table')],
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='main_edit_tournament')]
                                                    ])

table_list_edit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнирные таблицы 📋', callback_data='active_tournament_table')],
                                                    [InlineKeyboardButton(text = 'Архив 📚', callback_data='history_tournament_table')],
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='edit_tournament')]
                                                    ])

table_list_back = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='tournament_table')]])

create_exit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Создать турнир 🎾', callback_data='create_tournament')],
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='tournament_table')]
                                                    ])

# Вывод кнопок турнира
# tournament_info = bt.create_tournaments_keyboard(bt.get_list_tournaments())

# Вывод кнопок турнира для редактора
# tournament_info_editor = bt.create_tournaments_keyboard_editor(bt.get_list_tournaments_editor())

# Вывод кнопок под ссылку турнира
# active_tournament_table = bt.create_links_tournaments_keyboard(bt.get_links_tournaments())

# Вывод кнопок под ссылку турнира, которые попали в архив
# history_tournament_table = bt.create_links_tournaments_keyboard(bt.get_history_links_tournaments())

# Вывод кнопок под ссылку турнира для удаления игрока
# tournament_info_del_players = bt.create_tournaments_keyboard_players(bt.get_list_tournaments_players())

# Вывод кнопок для редактирования турнира
# tournament_info_edit = bt.create_tournaments_edit_keyboard(bt.get_list_tournaments_edit())

# Вывод кнопок для удаления турнира
# tournament_info_delete = bt.create_tournaments_delete_keyboard(bt.get_list_tournaments_delete())

confirm_delete_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='edit_tournament'),
                                                                InlineKeyboardButton(text = '✅ Подтвердить!', callback_data='delete_tournament_anyway')]
                                                                ])

reglament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='tournament_info'),
                                                 InlineKeyboardButton(text = '✅ Согласиться', callback_data='reglament_confirm')]
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

payment_address = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '✅ Я оплатил(-а)', callback_data='confirm_payment')],
                                                      [InlineKeyboardButton(text = 'Отменить и выйти', callback_data='start_message')]
                                                      ])

confirm_payment_pl = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = '❌ Отменить и выйти', callback_data='start_message')]])