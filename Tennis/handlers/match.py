import re
import os
import asyncio
from aiogram.types import CallbackQuery, LinkPreviewOptions, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import F, Router, types
from datetime import datetime

import keywords.kw_user as kb
import handlers.functions as f

from config.db import session
from models.User import User
from models.Division import Division
from models.Match import Match
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers

router = Router()

message_text_send = ''


@router.callback_query(F.data == 'match')
async def match(callback: CallbackQuery, bot):
    await callback.answer('')

    if await f.check_subscription(callback.from_user.id, bot):
        if os.path.exists("Tennis/img/match/match.jpg"):  # Проверка, есть ли файл
            photo = FSInputFile("Tennis/img/match/match.jpg")  # Загружаем файл
            await callback.message.answer_photo(photo, caption=f"<b>Поиск соперника</b> 🙋‍♂️🎾\n\nВ этом разделе игроки публикуют заявки на поиск соперника для игры.\nТы можешь откликнуться на уже созданную игру другим игроком или создать запрос на игру самостоятельно\n\n⚡️ Рекомендуем создавать заявку на поиск соперника с уже забронированым кортом", parse_mode=ParseMode.HTML, reply_markup=kb.players)
        else:
            await callback.message.answer(f"<b>Поиск соперника</b> 🙋‍♂️🎾\n\nВ этом разделе игроки публикуют заявки на поиск соперника для игры.\nТы можешь откликнуться на уже созданную игру другим игроком или создать запрос на игру самостоятельно\n\n⚡️ Рекомендуем создавать заявку на поиск соперника с уже забронированым кортом", parse_mode=ParseMode.HTML, reply_markup=kb.players)
    else:
        await f.check_subscription_message(callback)


@router.callback_query(F.data == 'search_match')
async def search_match(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')

    user_id = callback.from_user.id

    # Получаем все записи
    all_matches = session.query(Match).all()

    # Фильтруем те, у которых дата в прошлом
    expired_matches = [
        match for match in all_matches
        if (
            (match.date_booking and datetime.strptime(match.date_booking, "%H:%M %d.%m.%Y") < datetime.now()) or
            (match.date_without_booking and datetime.strptime(match.date_without_booking, "%H:%M %d.%m.%Y") < datetime.now())
        )
    ]

    # Удаляем их
    for match in expired_matches:
        session.delete(match)
        session.commit()

    tg_users_id = [row[0] for row in session.query(Match.id_tg_user).filter((Match.player_1 == None) & (Match.player_2 == None)).all()]
    count_users = len(tg_users_id)
    
    for user_tg in tg_users_id:
        if user_id == user_tg:
            count_users -= 1

    if count_users >= 1:
        await callback.message.answer(f"<b>Список доступных соперников</b> 👇", parse_mode=ParseMode.HTML) # сделать список отфильтрованным по уровню вашего дивизиона (если None у человека дивизион, то пусть видит все карточки соперников)
    
        options = LinkPreviewOptions(
            is_disabled=True
        )

        users = session.query(User).all()  # Получаем список объектов User
        users_matches = session.query(Match).filter((Match.player_1 == None) & (Match.player_2 == None)).all()
        sorted_matches = sorted(
            users_matches,
            key=lambda x: datetime.strptime(
                x.date_booking or x.date_without_booking,
                "%H:%M %d.%m.%Y"
            )
        )

        list_matches = ''
       
        for users_match in sorted_matches:
                for user in users:
                    if user.tg_user_id == user_id:
                        continue
                    elif user.tg_user_id == users_match.id_tg_user:
                        user_in_tournaments = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == user.tg_user_id).all()     # ИСПРАВИТЬ, ЧТОБЫ НЕ ОБРАЩАТЬСЯ К БД КАЖДЫЙ РАЗ
                        tournament_ids = [games.id_tournament for games in user_in_tournaments]  # Получаем список ID игроков
                        history_tournaments = session.query(Tournament).filter(Tournament.tournament_id.in_(tournament_ids)).all()         # ИСПРАВИТЬ, ЧТОБЫ НЕ ОБРАЩАТЬСЯ К БД КАЖДЫЙ РАЗ

                        history = '' 
                        division_lvl = ''

                        for toutnament in history_tournaments:
                            if history == '':
                                history += f"\"{toutnament.name_tournament}\""
                            else:
                                history += f", \"{toutnament.name_tournament}\""

                        if history == '':
                            history = 'Не участвовал(-а) 🥲'

                        if user.division_level != None:
                            name_division = session.query(Division).filter(Division.division_id == int(user.division_level)).first()
                            division_lvl = name_division.name_division
                        else:
                            division_lvl = 'Не определён'

                        if users_match.date_booking:
                            date = users_match.date_booking.split(" ")[1][:-5]
                        else:
                            date = users_match.date_without_booking.split(" ")[1][:-5]

                        # Добавить вывод рейтинга в скобках возле имени
                        # НЕ ИЗМЕНЯТЬ СООБЩЕНИЕ ! ! ! (это повлияет на функцию apply_match)
                        list_matches += f'\n\n🙋‍♂️ <b>{user.name_user.upper()}</b> ({date})\n\nСсылка: <tg-spoiler>{user.link}</tg-spoiler>\nИстория турниров: {history}\nДивизион: {division_lvl}\nПол: {user.sex}\nВозраст: {user.age}\n'
            
                        if users_match.date_booking:
                            list_matches += f'\nБронь корта: {users_match.date_booking}\nКорт: {users_match.name_court}\n'
                        else:
                            list_matches += f'\nБрони нет! Предлагаю поиграть: {users_match.date_without_booking}\n'

                        if users_match.comment:
                            list_matches += f'Комментарий: <blockquote>{users_match.comment}</blockquote>'

                        await callback.message.answer(list_matches, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.players_data)
                        list_matches = ''
    else:               
        await callback.message.answer(f"Нам жаль, но список 📂 доступных соперников пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.matches_not_found)
    


@router.callback_query(F.data == 'apply_match')
async def apply_match(callback: CallbackQuery, state:FSMContext, bot):

    user_id = callback.from_user.id

    message_text = callback.message.text or callback.message.caption  # Получаем текст сообщения

    # Поиск ссылки
    link_match = re.search(r'Ссылка:\s*(https://t\.me/\w+)', message_text)
    # Поиск даты
    date_match = re.search(r'(?:Бронь корта|Предлагаю поиграть):\s*(\d{2}:\d{2} \d{2}\.\d{2}\.\d{4})', message_text)

    if link_match and date_match:
        link = link_match.group(1)
        date = date_match.group(1)

        contestant = session.query(User).filter(User.link == link).first()
        user = session.query(User).filter(User.tg_user_id == user_id).first()

        if contestant:
            # НЕ ИЗМЕНЯТЬ СООБЩЕНИЕ ! ! ! (это повлияет на функцию accept_match)
            message_text_send = f"<b>Пользователь 🙋‍♂️ <a href='{user.link}'>{user.name_user}</a> откликнулся(-ась) на вашу заявку!</b>\n\n<b>ДЕТАЛИ ИГРЫ:</b>\n⏰ Дата игры: {date}\n🙋‍♂️ Соперник: <tg-spoiler>{user.link}</tg-spoiler>\n\n<b>СОПЕРНИК:</b>\n{user}"

            options = LinkPreviewOptions(
                is_disabled=True
            )

            try:
                await bot.send_message(chat_id=contestant.tg_user_id, text=message_text_send, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.apply_match)
                await callback.answer(f"✅ Заявка отправлена!", show_alert=False)
            except Exception as e:
                print(f"Не удалось отправить запрос на игру пользователю с id: {contestant.tg_user_id} из-за ошибки: {e}")
    else:
        await callback.answer('')
        print(f"Не удалось отправить запрос на игру от пользователя, т.к. в сообщении игры не распознана ссылка или дата. Текст игры: {message_text}")



@router.callback_query(F.data == 'accept_match')
async def accept_match(callback: types.CallbackQuery, state:FSMContext, bot):

    user_id = callback.from_user.id
    message_text = callback.message.text or callback.message.caption  # Получаем текст сообщения

    # Поиск ссылки
    link_match = re.search(r'Соперник:\s*(https://t\.me/\w+)', message_text)
    # Поиск даты
    date_match = re.search(r'Дата игры:\s*(\d{2}:\d{2} \d{2}\.\d{2}\.\d{4})', message_text)

    if link_match and date_match:
        link = link_match.group(1)
        date = date_match.group(1)
        
        user = session.query(User).filter(User.tg_user_id == user_id).first()
        contestant = session.query(User).filter(User.link == link).first()
        user_match = session.query(Match).filter((Match.id_tg_user == user_id) & ((Match.date_booking == date) | (Match.date_without_booking == date))).first()

        if contestant:
            options = LinkPreviewOptions(
                is_disabled=True
            )

            if user_match:
                if user_match.player_1 == None and user_match.player_2 == None:
                    print(f"✅ Игра подтверждена пользователем с id {user_id}!")
                    await callback.answer(f"✅ Игра объявлена!", show_alert=False)
                    await callback.message.answer("🏆")
                    await callback.message.answer(f"✅ <b>Игра объявлена!</b>\n\n• Ваша игра теперь доступна в разделе \"Мои подтверждённые игры 🎾\" для удобного поиска. Ваш соперник также получил уведомление о предстоящей игре\n\nГотовьтесь к встрече на корте {date}! ⚡️", parse_mode=ParseMode.HTML, reply_markup=kb.exit)
                    
                    message_text_send2 = f"✅ <b>Игра подтверждёна пользователем 🙋‍♂️ <a href='{user.link}'>{user.name_user}</a>!</b>\n\n<b>ДЕТАЛИ ИГРЫ:</b>\n⏰ Дата игры: {date}\n🙋‍♂️ Соперник: <tg-spoiler>{user.link}</tg-spoiler>\n\n<b>СОПЕРНИК:</b>\n{user}\n\n<blockquote>Ваша игра теперь доступна в разделе \"Мои подтверждённые игры 🎾\" для удобного поиска. Ваш соперник также получил уведомление о предстоящей игре</blockquote>\n\nГотовьтесь к встрече на корте! ⚡️"
                    try:

                        await bot.send_message(chat_id=contestant.tg_user_id, text="🏆")
                        await bot.send_message(chat_id=contestant.tg_user_id, text=message_text_send2, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.exit)
                        print("Подтверждение игры отправленно сопернику для информирования")
                    except Exception as e:
                        print(f"❌ Не удалось отправить сообщение о подтверждённой игре пользователю с id: {user_id} из-за ошибки: {e}")

                    user_match.player_1 = user.tg_user_id
                    user_match.player_2 = contestant.tg_user_id
                    session.commit()
                else:
                    confirm_contestant = session.query(User).filter(User.tg_user_id == user_match.player_2).first()
                    await callback.message.answer(f"❌ <b>Вы не можете принять эту игру, так как уже играете с <a href='{confirm_contestant.link}'>{confirm_contestant.name_user}</a> в это время!</b>", parse_mode=ParseMode.HTML, reply_markup=kb.confirm_match)
            else:
                print(f"❌ Матч не был найден в БД пользователя с id {user_id} и датой {date}!")


            # напоминание о игре
            time_before_match = datetime.strptime(date, "%H:%M %d.%m.%Y") - datetime.now()
            time_before_match = time_before_match.total_seconds()

            if time_before_match > 0:  # Проверяем, чтобы время было положительным
                await asyncio.sleep(time_before_match - 7200) # напоминание за 2 часа до начала

                options = LinkPreviewOptions(
                    is_disabled=True
                )

                text_notification = f"<b>Напоминание!</b>\n⚡️До игры с <a href='{user.link}'><b>{user.name_user}</b></a> осталось 2 часа"
                try:
                    await bot.send_message(chat_id=contestant.tg_user_id, text=text_notification, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.exit)
                    print("Отправлено напоминания пользователям об игре")
                except Exception as e:
                    print(f"Не удалось отправить напоминания пользователям об игре из-за ошибки: {e}")

                await callback.message.answer(f"<b>Напоминание!</b>\n⚡️До игры с <a href='{contestant.link}'><b>{contestant.name_user}</b></a> осталось 2 часа", parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.exit)
        
        else:
            print("❌ При попытке отправки подтверждения игры произошла ошибка! Ссылка игрока некорректная или игрока с такой ссылкой не существует!")

    else:
        print("❌ При попытке подтверждения игры произошла ошибка! Он не был найден из-за ошибки с ссылкой или датой!")
        await callback.answer('')

    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()



@router.callback_query(F.data == 'reject_match')
async def reject_match(callback: CallbackQuery):
    await callback.answer('')
    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()



@router.callback_query(F.data == 'my_match')
async def my_match(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')

    user_id = callback.from_user.id
    
    notification_sms = await callback.message.answer('⏰ Обновляем данные...')

    all_matches = session.query(Match).all()
    expired_matches = [
        match for match in all_matches
        if (
            (match.date_booking and datetime.strptime(match.date_booking, "%H:%M %d.%m.%Y") < datetime.now()) or
            (match.date_without_booking and datetime.strptime(match.date_without_booking, "%H:%M %d.%m.%Y") < datetime.now())
        )
    ]

    # Удаляем их
    for match in expired_matches:
        session.delete(match)
    session.commit()

    matches = session.query(Match).filter((Match.player_1 == user_id) | (Match.player_2 == user_id)).all()
    sorted_matches = sorted(
            matches,
            key=lambda x: datetime.strptime(
                x.date_booking or x.date_without_booking,
                "%H:%M %d.%m.%Y"
            )
        )

    if sorted_matches:
        for match in sorted_matches:
            user_id_player = ''

            if match.player_1 != user_id:
                user_id_player = match.player_1

            if match.player_2 != user_id:
                user_id_player = match.player_2

            if user_id_player:
                contestant = session.query(User).filter(User.tg_user_id == user_id_player).first()

                options = LinkPreviewOptions(
                    is_disabled=True
                )

                if match.date_booking != None:
                    date = match.date_booking

                if match.date_without_booking != None:
                    date = match.date_without_booking

                await notification_sms.edit_text(f"✅ <b>Игра с пользователем 🙋‍♂️ <a href='{contestant.link}'>{contestant.name_user}</a>!</b>\n\n<b>ДЕТАЛИ ИГРЫ:</b>\n⏰ Дата игры: {date}\n🙋‍♂️ Соперник: <tg-spoiler>{contestant.link}</tg-spoiler>\n\n<b>СОПЕРНИК:</b>\n{contestant}\nКорт: {match.name_court}\n\nГотовьтесь к встрече на корте! ⚡️", parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.my_matches)
    else:
        await notification_sms.edit_text(f"Список 📂 подтверждённых игр пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.my_matches)
