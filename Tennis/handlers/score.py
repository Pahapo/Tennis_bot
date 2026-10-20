import re
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram.exceptions import TelegramAPIError
from aiogram.enums import ParseMode
from aiogram import F, Router, types
from config.config import CHANNEL_SCORES

import keywords.kw_any as kb
import handlers.classes as cl
import handlers.validation as valid
import handlers.referrals as r

from config.db_utils import get_db_readonly, get_db
from sqlalchemy import select
from models.TournamentPlayers import TournamentPlayers
from models.Tournament import Tournament
from models.Division import Division
from models.User import User


router = Router()


@router.callback_query(F.data == 'score')
async def score(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await state.set_state(cl.FindUser.name_score)
    
    await callback.message.answer('<b>Тут вы можете записать счёт турнирной игры ⚡</b>\n\nВведите <b>username</b> соперника 👇', parse_mode=ParseMode.HTML)
    

@router.callback_query(F.data == 'find_users_for_score')
async def find_users_for_score(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')
    await state.set_state(cl.FindUser.name_score)
    
    await callback.message.answer('Введите <b>username</b> соперника 👇', parse_mode=ParseMode.HTML)


@router.message(cl.FindUser.name_score)
async def find_name_score(message: Message, state:FSMContext):

    await state.set_state(None)
    async with get_db_readonly() as session:  # Используем контекстный менеджер

        user_id = message.from_user.id
        link_finder_contestant = message.text.lower()

        if 'https://t.me/' not in link_finder_contestant:
            if '@' in link_finder_contestant:
                link_finder_contestant = link_finder_contestant.replace('@', '', 1)

            link_finder_contestant = 'https://t.me/' + link_finder_contestant

        await state.update_data(link_finder_contestant = link_finder_contestant)

        options = LinkPreviewOptions(
            is_disabled=True
        )

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
        user_tournaments = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == user_id))).all()

        if user_tournaments:
            tournament_ids = [tournament.id_tournament for tournament in user_tournaments]

        if user and tournament_ids:
            list_finder_user = (await session.scalars(select(User.link).join(TournamentPlayers, TournamentPlayers.id_tg_user == User.tg_user_id).where(TournamentPlayers.id_tournament.in_(tournament_ids),User.tg_user_id != user_id))).all()
            
            if link_finder_contestant in list_finder_user:
                user = (await session.scalars(select(User).where(User.link == link_finder_contestant))).first()

                await state.update_data(tg_user_id_kassa = user.tg_user_id)

                if user.division_level != None:
                    name_division = (await session.scalars(select(Division).where(Division.division_id == int(user.division_level)))).first()
                    division_lvl = name_division.name_division
                else:
                    division_lvl = 'Не определён'
                
                await message.answer(f'<b>Найден пользователь {user.name_user} 🙋‍♂️</b>\n\nСсылка: {user.link}\nДивизион: {division_lvl}', parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.edit_score)
            else:
                if link_finder_contestant == user.link:
                    await message.answer(f'<b>Вы не можете выбрать себя! 🙋‍♂️</b>', parse_mode=ParseMode.HTML, reply_markup=kb.back_score)
                else:
                    await message.answer(f'<b>Вы не можете выбрать этого игрока! 🙋‍♂️</b>\n\nИгрок не участвует с Вами в турнире', parse_mode=ParseMode.HTML, reply_markup=kb.back_score)
        else:
            await message.answer('Пользователь с таким <b>username</b> не найден в списке игроков турнира или не соответствует вашему дивизиону!',parse_mode=ParseMode.HTML, reply_markup=kb.back_score)



@router.callback_query(F.data == 'set_new_score')
async def set_new_score(callback: CallbackQuery, state:FSMContext):
    await callback.answer('')

    await state.set_state(cl.FindUser.score)
    await callback.message.answer(f'Укажите счёт в формате (<code>0:0 0:0</code>)\nЕсли было сыграно 3 сета, то в формате (<code>0:0 0:0 0:0</code>) 👇', parse_mode=ParseMode.HTML) 



@router.message(cl.FindUser.score)
async def find_score(message: Message, state:FSMContext):
    score = message.text

    if not valid.validate_score(score):
        remaining_chars = len(score) - 30
        await message.answer(f"⚠ Ошибка! Длина текста превышена на {remaining_chars} символов. Попробуйте снова 👇")
        return  # Останавливаем обработку

    if not valid.contains_link(score):
        await message.answer(f"⚠ Ошибка! Текст содержит ссылку. Попробуйте снова 👇")
        return  # Останавливаем обработку

    formatted_score = valid.auto_format_score(score)

    if not valid.is_valid_score_format(formatted_score):
        await message.answer(f"⚠ Ошибка! Текст неверного формата!\nВведите, например: 6:1 6:4 или 3-6 6-4 4-6\n\nПопробуйте снова 👇")

    await state.set_state(None)

    data = await state.get_data()
    user_id = message.from_user.id
    link_finder_contestant = data.get("link_finder_contestant")

    await state.update_data(score = formatted_score)
    
    async with get_db_readonly() as session:  # Используем контекстный менеджер
        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
        contestant = (await session.scalars(select(User).where(User.link == link_finder_contestant))).first()

        user_link = user.link
        user_name = '@' + user_link.replace("https://t.me/", "")
        contestant_link = contestant.link
        contestant_name = '@' + contestant_link.replace("https://t.me/", "")

        options = LinkPreviewOptions(
            is_disabled=True
        )

        await message.answer(f"<b>Подтвердите правильность введённых Вами данных 🎾</b>\n\n<b>Счёт между игроками турнира:</b>\n🙋‍♂️ <b>Игроки:</b> {user_name} vs {contestant_name}\n<b>⚡️ Счёт:</b> {score}", parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.confirm_score) 



@router.callback_query(F.data == 'confirm_score')
async def confirm_score(callback: CallbackQuery, state:FSMContext, bot):
    await callback.answer('')

    data = await state.get_data()
    user_id = callback.from_user.id
    link_finder_contestant = data.get("link_finder_contestant")
    score = data.get("score")

    async with get_db_readonly() as session:  # Используем контекстный менеджер
        
        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
        contestant = (await session.scalars(select(User).where(User.link == link_finder_contestant))).first()

        user_link = user.link
        user_name = '@' + user_link.replace("https://t.me/", "")
        contestant_link = contestant.link
        contestant_name = '@' + contestant_link.replace("https://t.me/", "")

        options = LinkPreviewOptions(
            is_disabled=True
        )

        if contestant:
            # НЕ ИЗМЕНЯТЬ СООБЩЕНИЕ ОТПРАВКИ ! ! ! (это повлияет на функцию handle_button_click_confirm_score)
            message_text_send = f"<b>Подтвердите счёт, записанный вашим <a href='{user.link}'>соперником</a></b>\n\n🙋‍♂️ <b>Игроки:</b> {user_name} vs {contestant_name}\n⚡️ <b>Счёт:</b> {score}"
            try:
                await bot.send_message(chat_id=contestant.tg_user_id, text=message_text_send, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.confirm_score_contestant)
                await callback.message.answer(f"<b>Запрос на подтверждение счёта отправлен! ⚡</b>\n\n• Ожидайте подтверждение со стороны соперника", parse_mode=ParseMode.HTML, reply_markup=kb.exit) 
            except Exception as e:
                print(f"⚠️ Не удалось отправить сообщение о счёте на турнире пользователю с id: {contestant.tg_user_id} из-за ошибки: {e}")
                await callback.message.answer(f'<b>Произошла ошибка при отправке счёта!</b>\n\n• Пожалуйста, свяжитесь с поддержкой бота! Их контакт есть в описании бота', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
        else:
            await callback.message.answer(f"<b>Запрос на подтверждение счёта не был отправлен!</b> Ошибка на стороне сервера!", parse_mode=ParseMode.HTML, reply_markup=kb.exit) 
            print(f"ОШИБКА! Пользователь с ссылкой '{link_finder_contestant}' не был найден в БД. Счёт не может быть отправлено сопернику!")  
    await state.clear()



@router.callback_query(F.data == 'handle_button_click_confirm_score')
async def handle_button_click_confirm_score(callback: types.CallbackQuery, bot: Bot):
    await callback.answer(f"✅ Счёт принят!", show_alert=False)

    message_text = callback.message.text
    match = re.search(r"(@[^\s]+) vs (@[^\s]+)\n.*? Счёт: ([\d: ]+)", message_text)  # Ищем нужные значения

    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()

    if match:
        contestant_name = match.group(1)  # Игрок 1
        user_name = match.group(2)        # Игрок 2
        score = match.group(3)            # Счёт
    
        async with get_db() as session:  # Используем контекстный менеджер

            contestant_link = contestant_name.replace("@", "https://t.me/")
            user_link = user_name.replace("@", "https://t.me/")
            user = (await session.scalars(select(User).where(User.link == user_link))).first()
            contestant = (await session.scalars(select(User).where(User.link == contestant_link))).first()

            contestant_tournament_pl = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == contestant.tg_user_id))).all()[-1]
            contestant_tournament = (await session.scalars(select(Tournament).where(Tournament.tournament_id == contestant_tournament_pl.id_tournament))).first()
            contestant_division = (await session.scalars(select(Division).where(Division.division_id == contestant.division_level))).first()

            options = LinkPreviewOptions(
                is_disabled=True
            )
            
            if contestant:
                message_text_send = f"<b><a href='{user.link}'>Соперник</a> подтвердил счёт Вашей с ним игры в турнире {contestant_tournament.name_tournament}!</b> 🙋‍♂️🎾"
                try:
                    await bot.send_message(chat_id=contestant.tg_user_id, text=message_text_send, link_preview_options=options, parse_mode=ParseMode.HTML, reply_markup=kb.exit)
                except Exception as e:
                    print(f"⚠️ Не удалось отправить сообщение о положительном ответом соперника на счёте. Пользователю с id: {contestant.tg_user_id} не отправилось сообщение из-за ошибки: {e}")
            

                # отправка сообщения в группу
                group_chat_id = CHANNEL_SCORES
                try:
                    message_text_send = f"<b>Турнир:</b> {contestant_tournament.name_tournament}\n<b>Дивизион:</b> {contestant_division.name_division}\n\n<b>Игроки:</b> <a href='{contestant.link}'>{contestant.name_user}</a> vs <a href='{user.link}'>{user.name_user}</a>\n<b>Счёт:</b> {score}"
                    await bot.send_message(chat_id=group_chat_id, text=message_text_send, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True)
                except TelegramAPIError as e:
                    print(f"Ошибка Telegram API: {e}")


                # изменение рейтинга после игры
                scores = re.findall(r'\b\d{1,2}:\d{1,2}\b', score)
                contestant_wins, user_wins = 0, 0

                for score_text in scores:
                    p1, p2 = map(int, score_text.split(":"))
                    contestant_wins += p1 > p2
                    user_wins += p2 > p1

                if contestant_wins == user_wins:
                    print("При выставлении счёта получилась - Ничья. Проверить!")
                    return

                winner, loser = (contestant, user) if contestant_wins > user_wins else (user, contestant)

                winner_rating = float(winner.rating)
                loser_rating = float(loser.rating)

                new_winner_rating, new_loser_rating = calculate_rating_change(winner_rating, loser_rating)

                if contestant_wins > user_wins:
                    print(f"Рейтинг пользователя \"{contestant.name_user}\" изменён с {winner_rating} на {new_winner_rating} из-за победы, а \"{user.name_user}\" изменён с {loser_rating} на {new_loser_rating} из-за проигрыша")
                elif user_wins > contestant_wins:
                    print(f"Рейтинг пользователя \"{user.name_user}\" изменён с {winner_rating} на {new_winner_rating} из-за победы, а \"{contestant.name_user}\" изменён с {loser_rating} на {new_loser_rating} из-за проигрыша")

                winner.rating = 5.99 if new_winner_rating > 5.99 else new_winner_rating
                loser.rating = 1.01 if new_loser_rating < 1.01 else new_loser_rating
                await session.commit()

                # По непонятной причине только когда разные дивизионы сражаются между собой, то рейтинг повышается только у дивизиона поменьше
                # Когда равные дивизионы, то всё работает как надо!

                await update_division_if_needed(winner, session, callback, bot)
                await update_division_if_needed(loser, session, callback, bot)

                # Первая игра приглашённого друга — награда тому, кто пригласил
                await r.reward_referral(winner.tg_user_id, session, bot)
                await r.reward_referral(loser.tg_user_id, session, bot)

            else:
                await callback.message.answer(f"<b>Запрос на подтверждение счёта не был отправлен!</b> Ошибка на стороне сервера!", parse_mode=ParseMode.HTML, reply_markup=kb.exit) 
                print(f"ОШИБКА! Пользователь с id '{contestant.tg_user_id}' не был найден в БД. Подтверждение счёта не может быть отправлено сопернику!")  
    else:
        print("❌ Данные не были обработаны при поиске данных при внесении счёта соперниками!")



def get_division_by_rating(rating: float) -> int:
    if 5.01 <= rating:
        return 1
    elif 4.01 <= rating <= 5.00:
        return 2
    elif 3.01 <= rating <= 4.00:
        return 3
    elif 2.01 <= rating <= 3.00:
        return 4
    else:
        return 5


async def update_division_if_needed(player, session, call, bot):
    new_division = get_division_by_rating(player.rating)

    if player.division_level != new_division:
        player.division_level = new_division
        try:
            division = await session.scalars(select(Division).where(Division.division_id == new_division))
            name = division.first().name_division if division else "Не определён"

            print(f"✅ Дивизион пользователя \"{player.tg_user_id}\" изменён на \"{name}\" автоматически")

            message_text = (
                f"<b>Дорогой игрок, сообщаем Вам о том, что Ваш дивизион изменён!</b> 🏆\n\nНовый дивизион: <b>{name}</b>\n\n<b>Поздравляем!</b> 🎉"
            )
            await bot.send_message(chat_id=player.tg_user_id, text=message_text, parse_mode=ParseMode.HTML, reply_markup=kb.exit)

        except Exception as e:
            print(f"⚠️ Не удалось отправить сообщение о смене дивизиона: {e}")



def calculate_rating_change(winner_rating, loser_rating, K=37):
    expected_score = 1 / (1 + 10 ** ((loser_rating - winner_rating)))
    new_winner = round((winner_rating * 400 + K * (1 - expected_score)) / 400, 2)
    new_loser = round((loser_rating * 400 - K * expected_score) / 400, 2)
    return new_winner, new_loser



@router.callback_query(F.data == 'unconfirm_score_contestant')
async def unconfirm_score_contestant(callback: types.CallbackQuery, bot):
    await callback.answer(f"❌ Счёт отменён!", show_alert=False)
    await callback.message.answer(f'<b>Хотите записать счёт самостоятельно? 🤔</b>', parse_mode=ParseMode.HTML, reply_markup=kb.another_score)

    user_id = callback.from_user.id
    message_text = callback.message.text
    match = re.search(r"(@[^\s]+) vs (@[^\s]+)\n.*? Счёт: ([\d: ]+)", message_text)  # Ищем нужные значения

    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()

    if match:
        contestant_name = match.group(1)  # Игрок 1
        
        async with get_db_readonly() as session:  # Используем контекстный менеджер

            contestant_name = contestant_name.replace("@", "https://t.me/")
            user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
            contestant = (await session.scalars(select(User).where(User.link == contestant_name))).first()

            options = LinkPreviewOptions(
                is_disabled=True
            )

            if contestant:
                message_text_send = f"<b>Соперник <a href='{user.link}'>{user.name_user}</a> НЕ подтвердил счёт Вашей с ним игры! 😥</b>"
                try:
                    await bot.send_message(chat_id=contestant.tg_user_id, text=message_text_send, link_preview_options=options, disable_web_page_preview=True, parse_mode=ParseMode.HTML, reply_markup=kb.exit)
                except Exception as e:
                    print(f"⚠️ Не удалось отправить сообщение о отрицательным ответом соперника на счёте. Пользователю с id: {contestant.tg_user_id} не отправилось сообщение из-за ошибки: {e}")
            else:
                await callback.message.answer(f"<b>Соперник не был найден!</b> Ошибка на стороне сервера!", parse_mode=ParseMode.HTML, reply_markup=kb.exit) 
                print(f"ОШИБКА! Пользователь с id '{contestant.tg_user_id}' не был найден в БД")  
    else:
        print("❌ Данные не были обработаны при поиске данных при внесении счёта соперниками!")



@router.callback_query(F.data == 'assign_initial_ratings')
async def assign_initial_ratings(callback: types.CallbackQuery, bot):

    await callback.answer(f"Начинаем выставлять рейтинг игрокам!", show_alert=False)
    
    def get_default_rating(level): return {1: 5.5, 2: 4.5, 3: 3.5, 4: 2.5}.get(level, 1.5)
    
    async with get_db() as session:  # Используем контекстный менеджер

        users = (await session.scalars(select(User))).all()
        for user in users:
            if user.rating is None and user.division_level is None:
                continue
            elif user.rating is None:
                user.rating = get_default_rating(user.division_level)
        await session.commit()
    await callback.message.answer(f"Закончили выставлять рейтинг игрокам!", reply_markup=kb.exit)

