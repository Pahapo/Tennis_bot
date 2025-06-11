from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import handlers.btn_tournaments as bt

exit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]])

tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Выйти', callback_data='start_message'),
                                                    InlineKeyboardButton(text = 'Изменить данные', callback_data='create_tournament')]
                                                    ])

tournaments_data = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Удалить участника ❌', callback_data='delete_players')],
                                                        [InlineKeyboardButton(text = 'Назад', callback_data='main_edit_tournament')]
                                                        ])

tournaments_data_exit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='main_edit_tournament')]])

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

confirm_delete_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='edit_tournament'),
                                                                InlineKeyboardButton(text = '✅ Подтвердить!', callback_data='delete_tournament_anyway')]
                                                                ])

reglament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='tournament_info'),
                                                 InlineKeyboardButton(text = '✅ Согласиться', callback_data='success_payment')] # ЗАМЕНИЛ (было reglament_confirm)
                                                 ])

level_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Золотой', callback_data='lvl_t_1')],
                                                        [InlineKeyboardButton(text = 'Серебряный', callback_data='lvl_t_2')],
                                                        [InlineKeyboardButton(text = 'Бронзовый', callback_data='lvl_t_3')],
                                                        [InlineKeyboardButton(text = 'Медный', callback_data='lvl_t_4')],
                                                        [InlineKeyboardButton(text = 'Железный', callback_data='lvl_t_5')],
                                                        [InlineKeyboardButton(text = 'Все дивизионы', callback_data='lvl_t_all')]
                                                        ])

type_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Одиночный', callback_data='type_t_1')],
                                                        [InlineKeyboardButton(text = 'Парный', callback_data='type_t_2')],
                                                        [InlineKeyboardButton(text = 'Микст', callback_data='type_t_3')]  # запятая
                                                        # [InlineKeyboardButton(text = 'Командный', callback_data='type_t_4')],
                                                        # [InlineKeyboardButton(text = 'Марафон', callback_data='type_t_5')],
                                                        # [InlineKeyboardButton(text = 'Короли тай-брейков', callback_data='type_t_6')]
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

# реферальная система

use_coins_q = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Да, использовать 💰', callback_data='use_coins')],
                                                  [InlineKeyboardButton(text = 'Назад', callback_data='reglament_confirm')]
                                                  ])