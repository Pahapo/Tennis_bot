import re
from aiogram.types import CallbackQuery, LinkPreviewOptions
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
        await callback.message.answer(f"<b>Тут ты можешь найти матч</b> 🙋‍♂️🎾\n\n• Создай свой, чтобы другие игроки могли найти тебя 👇", parse_mode=ParseMode.HTML, reply_markup=kb.players)
    else:
        await f.check_subscription_message(callback)


@router.callback_query(F.data == 'search_match')
async def search_match(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')

    data = await state.get_data()
    user_id = data.get("user_id") # взяли из состояния, которое записалось при /start

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

    tg_users_id = [row[0] for row in session.query(Match.id_tg_user).all()]
    count_users = len(tg_users_id)
    if user_id in tg_users_id:
        count_users -= 1

    if count_users >= 1:
        await callback.message.answer(f"Список доступных матчей 👇", parse_mode=ParseMode.HTML) # сделать список отфильтрованным по уровню вашего дивизиона (если None у человека дивизион, то пусть видит все карточки матчей)
    
        options = LinkPreviewOptions(
            is_disabled=True
        )

        users = session.query(User).all()  # Получаем список объектов User
        users_matches = session.query(Match).filter((Match.player_1 == None) & (Match.player_2 == None)).all()
        filtered_matches = list(filter(
            lambda match: (
                (match.date_booking is not None and datetime.strptime(match.date_booking, "%H:%M %d.%m.%Y") > datetime.today()) or
                (match.date_without_booking is not None and datetime.strptime(match.date_without_booking, "%H:%M %d.%m.%Y") > datetime.today())
            ),
            users_matches
        ))

        list_matches = ''
       
        for users_match in filtered_matches:
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

                        # Добавить вывод рейтинга в скобках возле имени
                        # НЕ ИЗМЕНЯТЬ СООБЩЕНИЕ ! ! ! (это повлияет на функцию apply_match)
                        list_matches += f'\n\n🙋‍♂️ <b>{user.name_user.upper()}</b>\n\nСсылка: <tg-spoiler>{user.link}</tg-spoiler>\nИстория турниров: {history}\nДивизион: {division_lvl}\nПол: {user.sex}\nВозраст: {user.age}\n'
            
                        if users_match.date_booking:
                            list_matches += f'Бронь корта: {users_match.date_booking}\n'
                        else:
                            list_matches += f'Брони нет! Предлагаю поиграть: {users_match.date_without_booking}\n'

                        if users_match.comment:
                            list_matches += f'Комментарий: <blockquote>{users_match.comment}</blockquote>'

                        await callback.message.answer(list_matches, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.players_data)
                        list_matches = ''
    else:               
        await callback.message.answer(f"Нам жаль, но список 📂 доступных матчей пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.matches_not_found)
    


@router.callback_query(F.data == 'apply_match')
async def apply_match(callback: CallbackQuery, state:FSMContext, bot):

    data = await state.get_data()
    user_id = data.get("user_id") # взяли из состояния, которое записалось при /start

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
            message_text_send = f"<b>Пользователь 🙋‍♂️ <a href='{user.link}'>{user.name_user}</a> откликнулся(-ась) на вашу заявку!</b>\n\n<b>ДЕТАЛИ МАТЧА:</b>\n⏰ Дата матча: {date}\n🙋‍♂️ Соперник: <tg-spoiler>{user.link}</tg-spoiler>\n\n<b>СОПЕРНИК:</b>\n{user}"

            options = LinkPreviewOptions(
                is_disabled=True
            )

            try:
                await bot.send_message(chat_id=contestant.tg_user_id, text=message_text_send, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.apply_match)
                await callback.answer(f"✅ Заявка отправлена!", show_alert=False)
            except Exception as e:
                print(f"Не удалось отправить запрос на матч пользователю с id: {contestant.tg_user_id} из-за ошибки: {e}")
    else:
        await callback.answer('')
        print(f"Не удалось отправить запрос на матч от пользователя, т.к. в сообщении матча не распознана ссылка или дата. Текст матча: {message_text}")



    # Добавить напоминание и фильтр при выводе

    # Добавить фото пользователя и отображать его в матчах


@router.callback_query(F.data == 'accept_match')
async def accept_match(callback: types.CallbackQuery, state:FSMContext, bot):

    data = await state.get_data()
    user_id = data.get("user_id")
    
    message_text = callback.message.text or callback.message.caption  # Получаем текст сообщения

    # Поиск ссылки
    link_match = re.search(r'Соперник:\s*(https://t\.me/\w+)', message_text)
    # Поиск даты
    date_match = re.search(r'Дата матча:\s*(\d{2}:\d{2} \d{2}\.\d{2}\.\d{4})', message_text)

    if link_match and date_match:
        link = link_match.group(1)
        date = date_match.group(1)
        
        user_match = session.query(Match).filter((Match.id_tg_user == user_id) & ((Match.date_booking == date) | (Match.date_without_booking == date))).first()
        user = session.query(User).filter(User.tg_user_id == user_id).first()
        contestant = session.query(User).filter(User.link == link).first()

        if contestant:
            options = LinkPreviewOptions(
                is_disabled=True
            )

            print(f"✅ Матч подтверждён пользователем с id {user_id}!")
            message_text_send2 = f"✅ <b>Матч подтверждён пользователем 🙋‍♂️ <a href='{user.link}'>{user.name_user}</a>!</b>\n\n<b>ДЕТАЛИ МАТЧА:</b>\n⏰ Дата матча: {date}\n🙋‍♂️ Соперник: <tg-spoiler>{user.link}</tg-spoiler>\n\n<b>СОПЕРНИК:</b>\n{user}\n\n<blockquote>Ваш матч теперь доступен в разделе \"Мои подтверждённые матчи 🎾\" для удобного поиска. Ваш соперник также получил уведомление о предстоящей игре</blockquote>\n\nГотовьтесь к встрече на корте! 🎾"
            
            try:
                await callback.answer(f"✅ Матч объявлен!!", show_alert=False)

                await bot.send_message(chat_id=contestant.tg_user_id, text="🏆")
                await bot.send_message(chat_id=contestant.tg_user_id, text=message_text_send2, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.exit)
                print("Подтверждение матча отправленно сопернику для информирования")
            except Exception as e:
                print(f"Не удалось отправить сообщение о подтверждённом матче пользователю с id: {user_id} из-за ошибки: {e}")

            await callback.message.answer("🏆")
            await callback.message.answer(f"✅ <b>Матч объявлен!</b>\n\n• Ваш матч теперь доступен в разделе \"Мои подтверждённые матчи 🎾\" для удобного поиска. Ваш соперник также получил уведомление о предстоящей игре\n\nГотовьтесь к встрече на корте {date}! 🎾", parse_mode=ParseMode.HTML, reply_markup=kb.exit)
            
            if user_match:
                user_match.player_1 = user.tg_user_id
                user_match.player_2 = contestant.tg_user_id
                session.commit()

            # if user_match:          # удалить
            #     session.delete(user_match)
            #     session.commit()
        
        else:
            print("❌ При попытке отправки подтверждения матча произошла ошибка! Ссылка игрока некорректная или игрока с такой ссылкой не существует!")

    else:
        print("❌ При попытке подтверждения матча произошла ошибка! Он не был найден из-за ошибки с ссылкой или датой!")
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

    data = await state.get_data()
    user_id = data.get("user_id")

    matches = session.query(Match).filter((Match.player_1 == user_id) | (Match.player_2 == user_id)).all()

    if matches:
        for match in matches:
            if len(matches) > 0:
                user_id_player = ''

                if match.player_1 != user_id:
                    user_id_player = match.player_1

                if match.player_2 != user_id:
                    user_id_player = match.player_2

                contestant = session.query(User).filter(User.tg_user_id == user_id_player).first()

                options = LinkPreviewOptions(
                    is_disabled=True
                )

                if match.date_booking != None:
                    date = match.date_booking

                if match.date_without_booking != None:
                    date = match.date_without_booking

                await callback.message.answer(f"✅ <b>Матч с пользователем 🙋‍♂️ <a href='{contestant.link}'>{contestant.name_user}</a>!</b>\n\n<b>ДЕТАЛИ МАТЧА:</b>\n⏰ Дата матча: {date}\n🙋‍♂️ Соперник: <tg-spoiler>{contestant.link}</tg-spoiler>\n\n<b>СОПЕРНИК:</b>\n{contestant}\n\nГотовьтесь к встрече на корте! 🎾", parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.my_matches)
            else: 
                await callback.message.answer(f"Список 📂 подтверждённых матчей пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.my_matches)
    else:
        print(f"Список подтверждённых матчей игрока с id ({user_id}) не отображается в разделе 'Мои подтверждённые матчи 🎾'")
