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

from config.db import session
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

    user = session.query(User).filter(User.tg_user_id == user_id).first()
    user_tournaments = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == user_id).all()

    tournament_ids = [tournament.id_tournament for tournament in user_tournaments]

    if user and tournament_ids:
        list_finder_user = [row[0] for row in session.query(User.link).join(TournamentPlayers, TournamentPlayers.id_tg_user == User.tg_user_id).filter(User.division_level == user.division_level, TournamentPlayers.id_tournament.in_(tournament_ids), User.tg_user_id != user_id).all()]

        if link_finder_contestant in list_finder_user:
            user = session.query(User).filter_by(link = link_finder_contestant).first()
            await state.update_data(tg_user_id_kassa = user.tg_user_id)

            if user.division_level != None:
                name_division = session.query(Division).filter(Division.division_id == int(user.division_level)).first()
                division_lvl = name_division.name_division
            else:
                division_lvl = 'Не определён'
            
            await message.answer(f'<b>Найден пользователь {user.name_user} 🙋‍♂️</b>\n\nСсылка: {user.link}\nДивизион: {division_lvl}', parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True, reply_markup=kb.edit_score)
        else:
            if link_finder_contestant == user.link:
                await message.answer(f'<b>Вы не можете выбрать себя! 🙋‍♂️</b>', parse_mode=ParseMode.HTML, reply_markup=kb.back_score)
            else:
                await message.answer(f'<b>Вы не можете выбрать этого игрока! 🙋‍♂️</b>\n\nОн не участвует с Вами в турнире', parse_mode=ParseMode.HTML, reply_markup=kb.back_score)
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
        remaining_chars = len(score) - 11
        await message.answer(f"⚠ Ошибка! Длина комментария превышена на {remaining_chars} символов. Попробуйте снова 👇")
        return  # Останавливаем обработку
    
    await state.set_state(None)

    data = await state.get_data()
    user_id = message.from_user.id
    link_finder_contestant = data.get("link_finder_contestant")

    await state.update_data(score = score)

    user = session.query(User).filter_by(tg_user_id = user_id).first()
    contestant = session.query(User).filter_by(link = link_finder_contestant).first()

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

    user = session.query(User).filter_by(tg_user_id = user_id).first()
    contestant = session.query(User).filter_by(link = link_finder_contestant).first()

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
            print(f"❌ Не удалось отправить сообщение о счёте на турнире пользователю с id: {contestant.tg_user_id} из-за ошибки: {e}")
            await callback.message.answer(f'<b>Произошла ошибка при отправке счёта!</b>\n\n• Пожалуйста, свяжитесь с поддержкой бота! Их контакт есть в описании бота', parse_mode=ParseMode.HTML, reply_markup=kb.exit)
    else:
        print(f"ОШИБКА! Пользователь с ссылкой '{link_finder_contestant}' не был наёден в БД. Счёт не может быть отправлен сопернику!")  
    await state.clear()



@router.callback_query(F.data == 'handle_button_click_confirm_score')
async def handle_button_click_confirm_score(callback: types.CallbackQuery, bot: Bot):
    await callback.answer(f"✅ Счёт принят!", show_alert=False)

    message_text = callback.message.text
    match = re.search(r"(@[^\s]+) vs (@[^\s]+)\n.*? Счёт: ([\d: ]+)", message_text)  # Ищем нужные значения

    if match:
        contestant_name = match.group(1)  # Игрок 1
        user_name = match.group(2)        # Игрок 2
        score = match.group(3)            # Счёт

        contestant_link = contestant_name.replace("@", "https://t.me/")
        user_link = user_name.replace("@", "https://t.me/")
        contestant = session.query(User).filter(User.link == contestant_link).first()
        user = session.query(User).filter(User.link == user_link).first()

        contestant_tournament_pl = session.query(TournamentPlayers).filter(TournamentPlayers.id_tg_user == contestant.tg_user_id).first()
        contestant_tournament = session.query(Tournament).filter(Tournament.tournament_id == contestant_tournament_pl.id_tournament).first()
        contestant_division = session.query(Division).filter(Division.division_id == contestant.division_level).first()

        options = LinkPreviewOptions(
            is_disabled=True
        )
        
        # отправка сообщения в группу
        group_chat_id = CHANNEL_SCORES  
        try:
            message_text_send = f"<b>Турнир:</b> {contestant_tournament.name_tournament}\n<b>Дивизион:</b> {contestant_division.name_division}\n\n<b>Игроки:</b> <a href='{user.link}'>{user.name_user}</a> vs <a href='{contestant.link}'>{contestant.name_user}</a>\n<b>Счёт:</b> {score}"
            await bot.send_message(chat_id=group_chat_id, text=message_text_send, parse_mode=ParseMode.HTML, link_preview_options=options, disable_web_page_preview=True)
        except TelegramAPIError as e:
            print(f"Ошибка Telegram API: {e}")

        if contestant:
            message_text_send = f"<b>Соперник подтвердил счёт Вашей с ним игры в турнире {contestant_tournament.name_tournament}!</b> 🙋‍♂️🎾"
            try:
                await bot.send_message(chat_id=contestant.tg_user_id, text=message_text_send, parse_mode=ParseMode.HTML, reply_markup=kb.exit)
            except Exception as e:
                print(f"❌ Не удалось отправить сообщение о положительном ответом соперника на счёте. Пользователю с id: {contestant.tg_user_id} не отправилось сообщение из-за ошибки: {e}")
        else:
            print(f"ОШИБКА! Пользователь с id '{contestant.tg_user_id}' не был наёден в БД. Подтверждение счёта не может быть отправлен сопернику!")  
    else:
        print("❌ Данные не были обработаны при поиске данных при внесении счёта соперниками!")

    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()



@router.callback_query(F.data == 'unconfirm_score_contestant')
async def unconfirm_score_contestant(callback: types.CallbackQuery, bot):
    await callback.answer(f"❌ Счёт отменён!", show_alert=False)
    await callback.message.answer(f'<b>Хотите записать счёт самостоятельно? 🤔</b>', parse_mode=ParseMode.HTML, reply_markup=kb.another_score)

    user_id = callback.from_user.id
    message_text = callback.message.text
    match = re.search(r"(@[^\s]+) vs (@[^\s]+)\n.*? Счёт: ([\d: ]+)", message_text)  # Ищем нужные значения

    if match:
        contestant_name = match.group(1)  # Игрок 1

        contestant_name = contestant_name.replace("@", "https://t.me/")
        user = session.query(User).filter(User.tg_user_id == user_id).first()
        contestant = session.query(User).filter(User.link == contestant_name).first()

        options = LinkPreviewOptions(
            is_disabled=True
        )

        if contestant:
            message_text_send = f"<b>Соперник <a href='{user.link}'>{user.name_user}</a> НЕ подтвердил счёт Вашей с ним игры! 😥</b>"
            try:
                await bot.send_message(chat_id=contestant.tg_user_id, text=message_text_send, link_preview_options=options, disable_web_page_preview=True, parse_mode=ParseMode.HTML, reply_markup=kb.exit)
            except Exception as e:
                print(f"❌ Не удалось отправить сообщение о отрицательным ответом соперника на счёте. Пользователю с id: {contestant.tg_user_id} не отправилось сообщение из-за ошибки: {e}")
        else:
            print(f"ОШИБКА! Пользователь с id '{contestant.tg_user_id}' не был наёден в БД")  
    else:
        print("❌ Данные не были обработаны при поиске данных при внесении счёта соперниками!")
    
    # Удаляем сообщение после нажатия на кнопку
    await callback.message.delete()
