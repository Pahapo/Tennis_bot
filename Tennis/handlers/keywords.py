from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL

import handlers.btn_tournaments as bt


# КНОПКИ


exit = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Главное меню', callback_data='start_message')]])

main_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')], # ЗАМЕНИТЬ
                                                [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
                                                [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                                                [InlineKeyboardButton(text = 'Приобрести инвентарь 🛒', callback_data='inventory')]
                                                ])

main_admin_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнирная таблица 📋', callback_data='tournament_table')],
                                                        [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
                                                        [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
                                                        [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                                                        [InlineKeyboardButton(text = 'Приобрести инвентарь 🛒', callback_data='inventory')],
                                                        [InlineKeyboardButton(text = 'ТЕСТИРОВАНИЕ', callback_data='testtesttest')], # изменить при тестировании новой функции!
                                                        [InlineKeyboardButton(text = 'Рассылка', callback_data='sending_messages')] # доделать рассылку (возможность прикреплять фото, ссылки)!
                                                        ])

main_edit_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнирная таблица 📋', callback_data='tournament_table')],
                                                        [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
                                                        [InlineKeyboardButton(text = 'Установить рейтинг 🥇', callback_data='set_division')], # сделать!
                                                        [InlineKeyboardButton(text = 'Выдать бан 🚫', callback_data='start_message')], # сделать!
                                                        [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
                                                        [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                                                        [InlineKeyboardButton(text = 'Приобрести инвентарь 🛒', callback_data='inventory')]
                                                        ])

edit_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнир 🏆', callback_data='edit_tournament')],
                                                [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
                                                [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                                                [InlineKeyboardButton(text = 'Приобрести инвентарь 🛒', callback_data='inventory')]
                                                ])

edit_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнирная таблица 📋', callback_data='tournament_table')],
                                                        [InlineKeyboardButton(text = 'Создать турнир 🎾', callback_data='register_tournament')],
                                                        [InlineKeyboardButton(text = 'Список турниров 📖', callback_data='tournament_lists')],
                                                        [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
                                                        [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                        ])

send_message_war = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='start_message'),
                                                        InlineKeyboardButton(text = '✅ Сделать рассылку!', callback_data='send_war')]
                                                        ])

send_message = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='start_message'),
                                                    InlineKeyboardButton(text = '✅ Подтвердить отправку!', callback_data='send')]
                                                    ])

builder = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Подписаться на канал", url=CHANNEL),
                                                InlineKeyboardButton(text="Я подписался", callback_data="check_subscription")]
                                                ])

tournament_info = bt.create_tournaments_keyboard(bt.get_list_tournaments())

reglament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='tournament_info'),
                                                    InlineKeyboardButton(text = 'Согласиться', callback_data='reglament_confirm')]
                                                    ])

reg_tournament_lvl = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Золотой 🥇', callback_data='lvl_p_1')],
                                                            [InlineKeyboardButton(text = 'Серебряный 🥈', callback_data='lvl_p_2')],
                                                            [InlineKeyboardButton(text = 'Бронзовый 🥉', callback_data='lvl_p_3')],
                                                            [InlineKeyboardButton(text = 'Медный 🎾', callback_data='lvl_p_4')],
                                                            [InlineKeyboardButton(text = 'Железный 🏃‍♂️', callback_data='lvl_p_5')],
                                                            [InlineKeyboardButton(text = 'Не знаю свой дивизион', callback_data='lvl_p_6')]
                                                            ])

level_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Золотой', callback_data='lvl_t_1')],
                                                        [InlineKeyboardButton(text = 'Серебряный', callback_data='lvl_t_2')],
                                                        [InlineKeyboardButton(text = 'Бронзовый', callback_data='lvl_t_3')],
                                                        [InlineKeyboardButton(text = 'Медный', callback_data='lvl_t_4')],
                                                        [InlineKeyboardButton(text = 'Железный', callback_data='lvl_t_5')],
                                                        [InlineKeyboardButton(text = 'Все дивизионы', callback_data='lvl_t_all')]
                                                        ])

reg_tournament_time1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Да', callback_data='time1_yes')],
                                                            [InlineKeyboardButton(text = 'Нет', callback_data='time1_no')]
                                                            ])

reg_tournament_time2 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Да', callback_data='time2_yes')],
                                                            [InlineKeyboardButton(text = 'Нет', callback_data='time2_no')]
                                                            ])

tournament_table = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Открыть таблицу 📋', url='https://docs.google.com/spreadsheets/d/1DdcB2aINDvH23RnMaWHBp4hDKTKP-VYlk82fowtZBHc/edit?usp=drivesdk')],
                                                         [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                         ])

court_reservation = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Забронировать корт 🎾', url='https://t.me/mw_tennis_bot')],
                                                         [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                         ])

address_court = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Северная Америка - Кижеватова 3Б', callback_data='court_1')],
                                                    [InlineKeyboardButton(text = 'Африка - Теслы 6', callback_data='court_2')],
                                                    [InlineKeyboardButton(text = 'Центральная Европа - Теслы 16', callback_data='court_3')],
                                                    [InlineKeyboardButton(text = 'Средиземноморский - Теслы 24', callback_data='court_4')],
                                                    [InlineKeyboardButton(text = 'Тропические острова - Лученка 24', callback_data='court_5')]
                                                    ])

players = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Выбрать соперника 🙋‍♂️', callback_data='search_contestant')],
                                                [InlineKeyboardButton(text = 'Моя карточка 📋', callback_data='get_data_player')],
                                                [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                ])

players_data = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='contestant')]])

tournaments_data = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='edit_tournament')]])

sex = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Мужчина', callback_data='men')],
                                            [InlineKeyboardButton(text = 'Женщина', callback_data='women')]
                                            ])

player = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='contestant'),
                                                InlineKeyboardButton(text = 'Изменить данные', callback_data='register_player')]
                                                ])

tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Выйти', callback_data='start_message'),
                                                    InlineKeyboardButton(text = 'Изменить данные', callback_data='register_tournament')]
                                                    ])

create_card = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Назад', callback_data='contestant'),
                                                    InlineKeyboardButton(text = 'Создать 📋', callback_data='register_player')]
                                                    ])

set_division = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Игроки без рейтинга 🙋‍♂️', callback_data='lvl_p_1')], # сделать!
                                                    [InlineKeyboardButton(text = 'Поиск игрока 🔍', callback_data='find_users')], # сделать!
                                                    [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                    ])
