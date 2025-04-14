from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.config import CHANNEL

main_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
                                                [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
                                                [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                                                [InlineKeyboardButton(text = 'Приобрести инвентарь 🛒', callback_data='inventory')]
                                                ])

main_admin_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнирная таблица 📋', callback_data='tournament_table')],
                                                        [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
                                                        [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
                                                        [InlineKeyboardButton(text = 'Выдать бан 🚫', callback_data='set_ban')],
                                                        [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                                                        [InlineKeyboardButton(text = 'Приобрести инвентарь 🛒', callback_data='inventory')],
                                                        [InlineKeyboardButton(text = 'ТЕСТИРОВАНИЕ', callback_data='testtesttest')], # изменить при тестировании новой функции!
                                                        [InlineKeyboardButton(text = 'Рассылка', callback_data='sending_messages')] # доделать рассылку (возможность прикреплять фото, ссылки)!
                                                        ])

main_edit_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнирная таблица 📋', callback_data='tournament_table')],
                                                        [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
                                                        [InlineKeyboardButton(text = 'Установить рейтинг 🥇', callback_data='set_division')], # сделать!
                                                        [InlineKeyboardButton(text = 'Выдать бан 🚫', callback_data='set_ban')],
                                                        [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
                                                        [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                                                        [InlineKeyboardButton(text = 'Приобрести инвентарь 🛒', callback_data='inventory')]
                                                        ])

edit_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнир 🏆', callback_data='edit_tournament')],
                                                [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
                                                [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                                                [InlineKeyboardButton(text = 'Приобрести инвентарь 🛒', callback_data='inventory')]
                                                ])

builder = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Подписаться на канал", url=CHANNEL),
                                                InlineKeyboardButton(text="Я подписался", callback_data="check_subscription")]
                                                ])
