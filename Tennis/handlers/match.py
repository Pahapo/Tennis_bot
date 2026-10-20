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
import handlers.match_app as ma

from config.db_utils import get_db_readonly, get_db
from sqlalchemy import select
from config.db import AsyncSessionLocal
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
            await callback.message.answer_photo(photo, caption=f"<b>Поиск соперника</b> 🙋‍♂️🎾\n\nВ этом разделе игроки публикуют заявки на поиск соперника для игры.\nТы можешь откликнуться на уже созданную игру другим игроком или создать запрос на игру самостоятельно\n\n⚡️ Рекомендуем создавать заявку на поиск соперника с уже забронированным кортом", parse_mode=ParseMode.HTML, reply_markup=kb.players)
        else:
            await callback.message.answer(f"<b>Поиск соперника</b> 🙋‍♂️🎾\n\nВ этом разделе игроки публикуют заявки на поиск соперника для игры.\nТы можешь откликнуться на уже созданную игру другим игроком или создать запрос на игру самостоятельно\n\n⚡️ Рекомендуем создавать заявку на поиск соперника с уже забронированным кортом", parse_mode=ParseMode.HTML, reply_markup=kb.players)
    else:
        await f.check_subscription_message(callback)


def parse_date_safe(date_str):
    if date_str:
        return datetime.strptime(date_str, "%H:%M %d.%m.%Y")
    else:
        return datetime.min  # или другая минимально возможная дата


@router.callback_query(F.data == 'search_match')
async def search_match(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')

    async with get_db() as session:  # Используем контекстный менеджер
        user_id = callback.from_user.id

        # Получаем все записи
        all_matches = (await session.scalars(select(Match))).all()

        # Фильтруем те, у которых дата в прошлом
        expired_matches = [
            match for match in all_matches
            if (
                (match.date_booking and datetime.strptime(match.date_booking, "%H:%M %d.%m.%Y") < datetime.now()) or
                (match.date_without_booking and datetime.strptime(match.date_without_booking, "%H:%M %d.%m.%Y") < datetime.now())
            )
        ]

        # Удаляем их (сыгранные игры оставляем — по ним нужен счёт)
        for match in expired_matches:
            if not ma.is_match_full(match):
                await session.delete(match)


    async with get_db_readonly() as session:  # Используем контекстный менеджер
        tg_users_id_1 = (await session.scalars(select(Match.id_tg_user).where((Match.type == "Одиночный") & (Match.player_2 == None)))).all()
        tg_users_id_2 = (await session.scalars(select(Match.id_tg_user).where((Match.type == "Парный") & (Match.player_4 == None)))).all()
        count_users = len(tg_users_id_1) + len(tg_users_id_2)
        tg_users_id = tg_users_id_1 + tg_users_id_2

        for user_tg in tg_users_id:
            if user_id == user_tg:
                count_users -= 1

        if count_users >= 1:
            await callback.message.answer(f"<b>Список доступных игр</b> 👇", parse_mode=ParseMode.HTML) # сделать список отфильтрованным по уровню дивизиона
        
            options = LinkPreviewOptions(
                is_disabled=True
            )

            users = (await session.scalars(select(User))).all()  # Получаем список объектов User

            users_matches = (await session.scalars(select(Match).where(((Match.type == "Одиночный") & (Match.player_2 == None)) | ((Match.type == "Парный") & (Match.player_4 == None))))).all()

            sorted_matches = sorted(users_matches, key=lambda x: parse_date_safe(x.date_booking or x.date_without_booking))
            list_matches = ''
        
            for users_match in sorted_matches:
                    for user in users:
                        if user.tg_user_id == user_id:
                            continue
                        elif user.tg_user_id == users_match.id_tg_user:
                            user_in_tournaments = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == user.tg_user_id))).all()     # ИСПРАВИТЬ, ЧТОБЫ НЕ ОБРАЩАТЬСЯ К БД КАЖДЫЙ РАЗ
                            tournament_ids = [games.id_tournament for games in user_in_tournaments]  # Получаем список ID игроков
                            history_tournaments = (await session.scalars(select(Tournament).where(Tournament.tournament_id.in_(tournament_ids)))).all()     # ИСПРАВИТЬ, ЧТОБЫ НЕ ОБРАЩАТЬСЯ К БД КАЖДЫЙ РАЗ

                            history = '' 
                            division_lvl = ''

                            for tournament in history_tournaments:
                                if history == '':
                                    history += f"\"{tournament.name_tournament}\""
                                else:
                                    history += f", \"{tournament.name_tournament}\""

                            if history == '':
                                history = 'Не участвовал(-а) 🥲'

                            if user.division_level != None:
                                name_division = (await session.scalars(select(Division).where(Division.division_id == int(user.division_level)))).first()
                                division_lvl = name_division.name_division
                            else:
                                division_lvl = 'Не определён'

                            if users_match.date_booking:
                                date = users_match.date_booking.split(" ")[1][:-5]
                            else:
                                date = users_match.date_without_booking.split(" ")[1][:-5]

                            # НЕ ИЗМЕНЯТЬ СООБЩЕНИЕ ! ! ! (это повлияет на функцию apply_match)
                            list_matches += f'\n\n🙋‍♂️ <b>{user.name_user.upper()}</b> ({date})\n\n<b>Ссылка:</b> <tg-spoiler>{user.link}</tg-spoiler>\n<b>История турниров:</b> {history}\n<b>Дивизион:</b> {division_lvl} ⚡️ {user.rating}\n<b>Пол:</b> {user.sex}\n<b>Возраст:</b> {user.age}\n'

                            if users_match.date_booking:
                                list_matches += f'\n✅ <b>Бронь корта:</b> {users_match.date_booking}\nКорт: {users_match.name_court}\n'
                            else:
                                list_matches += f'\n❌ <b>Брони нет! Предлагаю поиграть:</b> {users_match.date_without_booking}\n'

                            if users_match.type:
                                list_matches += f'<b>Тип игры:</b> {users_match.type}\n'

                            if users_match.comment:
                                list_matches += f'<b>Комментарий:</b> <blockquote>{users_match.comment}</blockquote>'

                            await callback.message.answer(list_matches, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.players_data)
                            list_matches = ''
        else:               
            await callback.message.answer(f"Нам жаль, но список 📂 доступных соперников пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.matches_not_found)
        


@router.callback_query(F.data == 'apply_match')
async def apply_match(callback: CallbackQuery, state:FSMContext, bot):
    async with get_db_readonly() as session:  # Используем контекстный менеджер

        user_id = callback.from_user.id
        message_text = callback.message.text or callback.message.caption  # Получаем текст сообщения

        # Поиск ссылки
        link_match = re.search(r'Ссылка:\s*(https://t\.me/\w+)', message_text)
        # Поиск даты
        date_match = re.search(r'(?:Бронь корта|Предлагаю поиграть):\s*(\d{2}:\d{2} \d{2}\.\d{2}\.\d{4})', message_text)

        if link_match and date_match:
            link = link_match.group(1)
            date = date_match.group(1)

            user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
            contestant = (await session.scalars(select(User).where(User.link == link))).first()

            if contestant:
                # НЕ ИЗМЕНЯТЬ СООБЩЕНИЕ ! ! ! (это повлияет на функцию accept_match)
                message_text_send = f"<b>Пользователь 🙋‍♂️ <a href='{user.link}'>{user.name_user}</a> откликнулся(-ась) на вашу заявку!</b>\n\n<b>ДЕТАЛИ ИГРЫ:</b>\n⏰ Дата игры: {date}\n🙋‍♂️ Соперник: <tg-spoiler>{user.link}</tg-spoiler>\n\n<b>СОПЕРНИК:</b>\n{(await user.build_repr_data())}"

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
    async with get_db() as session:  # Используем контекстный менеджер

        user_id = callback.from_user.id
        message_text = callback.message.text or callback.message.caption  # Получаем текст сообщения

        # Поиск ссылки
        link_match = re.search(r'Соперник:\s*(https://t\.me/\w+)', message_text)
        # Поиск даты
        date_match = re.search(r'Дата игры:\s*(\d{2}:\d{2} \d{2}\.\d{2}\.\d{4})', message_text)

        # Удаляем сообщение после нажатия на кнопку
        await callback.message.delete()

        if link_match and date_match:
            link = link_match.group(1)
            date = date_match.group(1)
            
            user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
            contestant = (await session.scalars(select(User).where(User.link == link))).first()
            user_match = (await session.scalars(select(Match).where((Match.id_tg_user == user_id) & ((Match.date_booking == date) | (Match.date_without_booking == date))))).first()

            if contestant:
                options = LinkPreviewOptions(
                    is_disabled=True
                )

                if user_match:
                    if user_match.type == "Одиночный" and user_match.player_2 == None:
                        if user_match.player_2 != contestant.tg_user_id:
                            type_match = 'одиночной'
                            try:
                                print(f"✅ Игра подтверждена пользователем с id {user_id} с игроком с id {contestant.tg_user_id}!")
                                await callback.answer(f"✅ Игра объявлена!", show_alert=False)
                                await callback.message.answer("🏆")
                                await callback.message.answer(f"✅ <b>Игра объявлена!</b>\n\n• Ваша игра теперь доступна в разделе \"Мои подтверждённые игры 🎾\" для удобного поиска. Ваш соперник также получил уведомление о предстоящей игре\n\nГотовьтесь к встрече на корте {date}! ⚡️", parse_mode=ParseMode.HTML, reply_markup=kb.exit)
                                
                                message_text_send2 = f"✅ <b>Игра подтверждёна пользователем 🙋‍♂️ <a href='{user.link}'>{user.name_user}</a>!</b>\n\n<b>ДЕТАЛИ ИГРЫ:</b>\n⏰ Дата игры: {date}\n🙋‍♂️ Соперник: <tg-spoiler>{user.link}</tg-spoiler>\n\n<b>СОПЕРНИК:</b>\n{(await user.build_repr_data())}\n\n<blockquote>Ваша игра теперь доступна в разделе \"Мои подтверждённые игры 🎾\" для удобного поиска. Ваш соперник также получил уведомление о предстоящей игре</blockquote>\n\nГотовьтесь к встрече на корте! ⚡️"
                                
                                if user_match.player_2 == None:
                                    user_match.player_2 = contestant.tg_user_id
                                await session.commit()
                            
                                await bot.send_message(chat_id=contestant.tg_user_id, text="🏆")
                                await bot.send_message(chat_id=contestant.tg_user_id, text=message_text_send2, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.exit)
                            except Exception as e:
                                print(f"⚠️ Не удалось отправить сообщение о подтверждённой игре пользователю с id: {user_id} из-за ошибки: {e}")

                            # Напоминание за 2 часа до игры и запрос счёта отправляет планировщик (handlers/match_app.py)
                            return
                        else:
                            await callback.message.answer(f"❌ <b>Вы не можете принять эту игру</b>\n\nВы уже приняли приглашение от этого пользователя! Проверьте Ваши 'подтверждённые игры 🎾'</b>", parse_mode=ParseMode.HTML, reply_markup=kb.confirm_match)

                    if user_match.type == "Парный" and user_match.player_4 == None:
                        type_match = 'парной'
                        if user_match.player_2 != contestant.tg_user_id or user_match.player_3 != contestant.tg_user_id:
                            try:
                                print(f"✅ Игра подтверждена пользователем с id {user_id} с игроком с id {contestant.tg_user_id}!")
                                await callback.answer(f"✅ Игра объявлена!", show_alert=False)
                                await callback.message.answer("🏆")
                                await callback.message.answer(f"✅ <b>Игра объявлена!</b>\n\n• Ваша игра теперь доступна в разделе \"Мои подтверждённые игры 🎾\" для удобного поиска. Ваш соперник также получил уведомление о предстоящей игре\n\nГотовьтесь к встрече на корте {date}! ⚡️", parse_mode=ParseMode.HTML, reply_markup=kb.exit)
                                
                                message_text_send2 = f"✅ <b>Игра подтверждёна пользователем 🙋‍♂️ <a href='{user.link}'>{user.name_user}</a>!</b>\n\n<b>ДЕТАЛИ ИГРЫ:</b>\n⏰ Дата игры: {date}\n🙋‍♂️ Соперник: <tg-spoiler>{user.link}</tg-spoiler>\n\n<b>СОПЕРНИК:</b>\n{(await user.build_repr_data())}\n\n<blockquote>Ваша игра теперь доступна в разделе \"Мои подтверждённые игры 🎾\" для удобного поиска. Ваш соперник также получил уведомление о предстоящей игре</blockquote>\n\nГотовьтесь к встрече на корте! ⚡️"
                                
                                if user_match.player_2 == None:
                                    user_match.player_2 = contestant.tg_user_id
                                elif user_match.player_3 == None:
                                    user_match.player_3 = contestant.tg_user_id
                                elif user_match.player_4 == None:
                                    user_match.player_4 = contestant.tg_user_id
                                await session.commit()

                                await bot.send_message(chat_id=contestant.tg_user_id, text="🏆")
                                await bot.send_message(chat_id=contestant.tg_user_id, text=message_text_send2, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.exit)
                            except Exception as e:
                                print(f"⚠️ Не удалось отправить сообщение о подтверждённой игре пользователю с id: {user_id} из-за ошибки: {e}")

                            # Напоминание за 2 часа до игры и запрос счёта отправляет планировщик (handlers/match_app.py)
                            return
                        else:
                            await callback.message.answer(f"❌ <b>Вы не можете принять эту игру</b>\n\nВы уже приняли приглашение от этого пользователя! Проверьте Ваши 'подтверждённые игры 🎾'</b>", parse_mode=ParseMode.HTML, reply_markup=kb.confirm_match)

                    else:
                        await callback.message.answer(f"❌ <b>Вы не можете принять эту игру, так как уже играете с другими игроками!</b>", parse_mode=ParseMode.HTML, reply_markup=kb.confirm_match)
                else:
                    print(f"❌ Матч не был найден в БД пользователя с id {user_id} и датой {date}!")
        
            else:
                print("❌ При попытке отправки подтверждения игры произошла ошибка! Ссылка игрока некорректная или игрока с такой ссылкой не существует!")

        else:
            print("❌ При попытке подтверждения игры произошла ошибка! Он не был найден из-за ошибки с ссылкой или датой!")
            await callback.answer('')



@router.callback_query(F.data == 'reject_match')
async def reject_match(callback: CallbackQuery):
    await callback.answer('')
    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()



@router.callback_query(F.data == 'my_match')
async def my_match(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    async with get_db() as session:  # Используем контекстный менеджер

        user_id = callback.from_user.id
        
        all_matches = (await session.scalars(select(Match))).all()

        expired_matches = [
            match for match in all_matches
            if (
                (match.date_booking and datetime.strptime(match.date_booking, "%H:%M %d.%m.%Y") < datetime.now()) or
                (match.date_without_booking and datetime.strptime(match.date_without_booking, "%H:%M %d.%m.%Y") < datetime.now())
            )
        ]

        # Удаляем их
        try:
            for match in expired_matches:
                if not ma.is_match_full(match):  # Сыгранные игры оставляем — по ним нужен счёт
                    await session.delete(match)
        except Exception as e:
            # обработка ошибки
            print(f"Произошла ошибка: {e}")

        matches = (await session.scalars(select(Match).where(
            ((Match.type == 'Одиночный') & (Match.player_1 == user_id) & (Match.player_2 != None)) |
            ((Match.type == 'Одиночный') & (Match.player_1 != None) & (Match.player_2 == user_id)) |
            ((Match.type == 'Парный') & (Match.player_1 == user_id) & (Match.player_2 != None)) |
            ((Match.type == 'Парный') & (Match.player_2 == user_id) & (Match.player_1 != None)) |
            ((Match.type == 'Парный') & (Match.player_3 == user_id) & (Match.player_1 != None) & (Match.player_2 != None)) |
            ((Match.type == 'Парный') & (Match.player_4 == user_id) & (Match.player_1 != None) & (Match.player_2 != None) & (Match.player_3 != None))
        ))).all()
        
        sorted_matches = sorted(matches, key=lambda x: parse_date_safe(x.date_booking or x.date_without_booking))

        if sorted_matches:
            for match in sorted_matches:
                user_id_player = []

                if match.player_1 != user_id and match.player_1 != None:
                    user_id_player.append(match.player_1)
                if match.player_2 != user_id and match.player_2 != None:
                    user_id_player.append(match.player_2)
                if match.player_3 != user_id and match.player_3 != None:
                    user_id_player.append(match.player_3)
                if match.player_4 != user_id and match.player_4 != None:
                    user_id_player.append(match.player_4)

                if user_id_player:
                    contestants = []
                    for i in range(len(user_id_player)):
                        contestants.append((await session.scalars(select(User).where(User.tg_user_id == user_id_player[i]))).first())

                    options = LinkPreviewOptions(
                        is_disabled=True
                    )

                    if match.date_booking != None:
                        date = match.date_booking

                    if match.date_without_booking != None:
                        date = match.date_without_booking

                    if match.type == 'Одиночный':
                        if match.name_court:
                            court_name = match.name_court
                        else:
                            court_name = "бронь отсутствует"
                        await callback.message.answer(f"✅ <b>Игра с пользователем 🙋‍♂️ <a href='{contestants[0].link}'>{contestants[0].name_user}</a>!</b>\n\n<b>ДЕТАЛИ ИГРЫ:</b>\n⏰ Дата игры: {date}\n🙋‍♂️ Соперник: <tg-spoiler>{contestants[0].link}</tg-spoiler>\n\n<b>СОПЕРНИК:</b>\n{(await contestants[0].build_repr_data())}\n\n📍 Корт: {court_name}\n🔗 Тип игры: {match.type}\n\nГотовьтесь к встрече на корте! ⚡️", parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.my_matches)
                    else:
                        users_name_list = ''
                        for contestant in contestants:
                            users_name_list += f" <a href='{contestant.link}'>{contestant.name_user}</a>"

                        users_list = ''
                        for contestant in contestants:
                            users_list += f"\n🙋‍♂️ {contestant}\n"

                        users_link_list = ''
                        for contestant in contestants:
                            users_link_list += f"\n<tg-spoiler>{contestant.link}</tg-spoiler>"

                        await callback.message.answer(f"✅ <b>Игра с пользователями 🙋‍♂️🙋‍♂️{users_name_list}!</b>\n\n<b>ДЕТАЛИ ИГРЫ:</b>\n⏰ Дата игры: {date}\n🙋‍♂️🙋‍♂️ Соперники: {users_link_list}\n\n<b>СОПЕРНИКИ:</b>{users_list}\n📍 Корт: {match.name_court}\n🔗 Тип игры: {match.type}\n\nГотовьтесь к встрече на корте! ⚡️", parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.my_matches)

        else:
            await callback.message.answer(f"Список 📂 подтверждённых игр пока пуст", parse_mode=ParseMode.HTML, reply_markup=kb.my_matches)
