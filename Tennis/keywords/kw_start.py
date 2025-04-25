from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.config import CHANNEL

# Администраторы

main_admin_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнир 🏆', callback_data='main_edit_tournament')],
                                                       [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
                                                       [InlineKeyboardButton(text = 'Выдать бан 🚫', callback_data='set_ban')],
                                                       [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                                                       [InlineKeyboardButton(text = 'Барахолка 🛒', callback_data='inventory')],
                                                       [InlineKeyboardButton(text = 'ТЕСТИРОВАНИЕ', callback_data='testtesttest')], # изменить при тестировании новой функции!
                                                       [InlineKeyboardButton(text = 'Рассылка', callback_data='sending_messages')] # доделать рассылку (возможность прикреплять фото)!
                                                       ])
# Главные редакторы

main_edit_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнир 🏆', callback_data='main_edit_tournament')],
                                                      [InlineKeyboardButton(text = 'Дивизион 🥇 / Бан 🚫', callback_data='main_edit_level_ban')],
                                                      [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
                                                      [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                                                      [InlineKeyboardButton(text = 'Барахолка 🛒', callback_data='inventory')]
                                                      ])

main_edit_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнирные таблицы 📋', callback_data='tournament_table')],
                                                            [InlineKeyboardButton(text = 'Список турниров/участников 📖', callback_data='tournament_lists')],
                                                            [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
                                                            [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                            ])

main_edit_level_ban = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Установить дивизион 🥇', callback_data='set_division')],
                                                            [InlineKeyboardButton(text = 'Выдать бан 🚫', callback_data='set_ban')],
                                                            [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                            ])

# Редакторы

edit_btn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Турнир 🏆', callback_data='edit_tournament')],
                                                [InlineKeyboardButton(text = 'Поиск соперника 🙋‍♂️', callback_data='contestant')],
                                                [InlineKeyboardButton(text = 'Забронировать корт 🎾', callback_data='court_reservation')],
                                                [InlineKeyboardButton(text = 'Барахолка 🛒', callback_data='inventory')]
                                                ])

edit_tournament = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Создать турнир 🎾', callback_data='create_tournament')],
                                                        [InlineKeyboardButton(text = 'Турнирные таблицы 📋', callback_data='tournament_table')],
                                                        [InlineKeyboardButton(text = 'Список турниров/участников 📖', callback_data='tournament_lists')],
                                                        [InlineKeyboardButton(text = 'Редактировать турнир ⚙️', callback_data='tournament_edit')],
                                                        [InlineKeyboardButton(text = 'Удалить турнир 🚫', callback_data='delete_tournament')],
                                                        [InlineKeyboardButton(text = 'Запись на турнир 🏆', callback_data='tournament_info')],
                                                        [InlineKeyboardButton(text = 'Назад', callback_data='start_message')]
                                                        ])

builder = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Подписаться на канал", url=CHANNEL),
                                                InlineKeyboardButton(text="Я подписался", callback_data="check_subscription")]
                                                ])
