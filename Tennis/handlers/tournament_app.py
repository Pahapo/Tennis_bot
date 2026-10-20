import re
import asyncio
from html import escape, unescape
from datetime import datetime, timedelta
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from config.config import EDITOR, MAIN_EDITOR, ADMINS

import keywords.kw_any as ka
import handlers.gold as g
import handlers.functions as f
import handlers.match_app as ma
import googleSheet.googleSheet as gs

from config.db_utils import get_db
from sqlalchemy import select, func
from models.User import User
from models.Division import Division
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers
from models.Payment import Payment
from models.PaymentRequest import PaymentRequest

# Турниры из Mini App: запись, проверка чека редактором, счёт турнирной игры

router = Router()

MIN_CRYSTALS = 300          # Меньше 300 кристаллов применить нельзя
CRYSTALS_PER_RUBLE = 100    # 100 кристаллов = 1 бел.руб.


# ---------- Вспомогательные функции ----------

def clean_html(text):  # Регламент хранится с HTML-тегами для Telegram — в приложении показываем просто текст
    return unescape(re.sub(r'<[^>]+>', '', text or ''))


def parse_day(text):  # "20.05.2026" -> datetime (или None)
    try:
        return datetime.strptime(text, "%d.%m.%Y")
    except (ValueError, TypeError):
        return None


def is_staff(user_id):  # Редакторы и админы не могут применять кристаллы (как в боте)
    return user_id in EDITOR or user_id in MAIN_EDITOR or user_id in ADMINS


def get_crystals(user):  # В БД кристаллы хранятся строкой
    if user.coins:
        return int(user.coins)
    return 0


def price_with_crystals(price, crystals):  # Стоимость участия с учётом кристаллов
    return round(price - crystals / CRYSTALS_PER_RUBLE, 1)


def check_crystals(crystals, balance, price):  # Текст ошибки или None, если всё хорошо
    if crystals == 0:
        return None
    if crystals < MIN_CRYSTALS:
        return f'Можно применить от {MIN_CRYSTALS} 💎'
    if crystals > balance:
        return 'У вас недостаточно кристаллов'
    if crystals / CRYSTALS_PER_RUBLE >= price * 0.5:
        return 'Скидка кристаллами должна быть меньше половины стоимости'
    return None


async def get_division_names(session: AsyncSession):  # {division_id: название}
    divisions = (await session.scalars(select(Division))).all()
    names = {}
    for division in divisions:
        names[division.division_id] = division.name_division
    return names


async def count_players_in_division(tournament_id, division_level, session: AsyncSession):  # Сколько игроков этого дивизиона уже в турнире
    return await session.scalar(select(func.count()).select_from(TournamentPlayers).join(User, TournamentPlayers.id_tg_user == User.tg_user_id).where(
        (TournamentPlayers.id_tournament == tournament_id) & (User.division_level == division_level)
    ))


async def tournament_status(tournament, user, session: AsyncSession):  # Можно ли записаться: (статус, дивизион для записи)
    divisions = list(map(int, tournament.division.split(",")))

    registrations = await session.scalar(select(func.count()).select_from(TournamentPlayers).where(
        (TournamentPlayers.id_tournament == tournament.tournament_id) & (TournamentPlayers.id_tg_user == user.tg_user_id)
    ))

    pending = (await session.scalars(select(PaymentRequest).where(
        (PaymentRequest.tournament_id == tournament.tournament_id) & (PaymentRequest.tg_user_id == user.tg_user_id) & (PaymentRequest.status == 'pending')
    ))).first()

    if pending:
        return 'pending', None
    if user.ban_status == True:
        return 'banned', None
    if user.division_level == None:
        return 'no_division', None
    if registrations >= 2:
        return 'registered', None

    # Уже участвует — можно сыграть ещё в одном дивизионе (на 1 выше), если он есть в турнире
    if registrations == 1:
        second = user.division_level - 1
        if user.division_level > 1 and second in divisions:
            if await count_players_in_division(tournament.tournament_id, second, session) < tournament.quantity_person:
                return 'can_register_second', second
        return 'registered', None

    if user.division_level not in divisions:
        return 'wrong_division', None
    if await count_players_in_division(tournament.tournament_id, user.division_level, session) >= tournament.quantity_person:
        return 'full', None

    return 'can_register', user.division_level


def is_open(tournament):  # Запись ещё идёт (как в боте: старт сегодня или позже)
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    start = parse_day(tournament.start_tournament)
    return start != None and start >= today


async def get_open_tournaments(session: AsyncSession):  # Турниры, на которые ещё идёт запись
    tournaments = (await session.scalars(select(Tournament))).all()

    result = []
    for tournament in tournaments:
        if is_open(tournament):
            result.append(tournament)
    return result


async def get_running_tournaments(user_id, session: AsyncSession):  # Мои турниры, которые уже идут (для записи счёта)
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    my_rows = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == user_id))).all()
    tournament_ids = []
    for row in my_rows:
        if row.id_tournament not in tournament_ids:
            tournament_ids.append(row.id_tournament)

    result = []
    if tournament_ids:
        tournaments = (await session.scalars(select(Tournament).where(Tournament.tournament_id.in_(tournament_ids)))).all()
        for tournament in tournaments:
            start = parse_day(tournament.start_tournament)
            end = parse_day(tournament.end_tournament)
            if start and start <= today and (end == None or end >= today - timedelta(days=3)):
                result.append(tournament)
    return result


async def send_tournament_score(user, contestant, score, bot):  # Счёт турнирной игры сопернику на подтверждение
    user_name = '@' + user.link.replace("https://t.me/", "")
    contestant_name = '@' + contestant.link.replace("https://t.me/", "")

    # НЕ ИЗМЕНЯТЬ СООБЩЕНИЕ ОТПРАВКИ ! ! ! Это тот же текст, что в handlers/score.py — его разбирает handle_button_click_confirm_score
    message_text_send = f"<b>Подтвердите счёт, записанный вашим <a href='{user.link}'>соперником</a></b>\n\n🙋‍♂️ <b>Игроки:</b> {user_name} vs {contestant_name}\n⚡️ <b>Счёт:</b> {score}"
    await ma.notify(bot, contestant.tg_user_id, message_text_send, ka.confirm_score_contestant)


# ---------- Проверка чека редактором ----------

async def send_payment_to_editors(request, user, tournament, division_name, photo_path, bot):  # Чек из приложения — каждому редактору
    discount = round((tournament.price or 0) - request.price, 1)

    text = f"<b>Подтвердите оплату пользователя <a href='{escape(user.link or '')}'>{escape(user.name_user or '')}</a></b> (из приложения)\n\n🏆 <b>Турнир:</b> {escape(tournament.name_tournament)}\n💪 <b>Дивизион:</b> {division_name}\n💰 <b>Оплачено:</b> {request.price} бел.руб."
    if request.crystals > 0:
        text += f"\n💎 <b>Скидка кристаллами:</b> {discount} бел.руб. ({request.crystals} 💎)"
    text += f"\n\n<b>ID заявки:</b> {request.id_request}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Оплата не получена', callback_data=f'app_pay_no:{request.id_request}')],
                                                     [InlineKeyboardButton(text='✅ Подтвердить оплату!', callback_data=f'app_pay_ok:{request.id_request}')]])

    for editor in EDITOR:
        try:
            await bot.send_photo(chat_id=editor, photo=FSInputFile(photo_path), caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        except Exception as e:
            print(f"⚠️ Не удалось отправить чек редактору {editor}: {e}")


# Кнопка редактора "✅ Подтвердить оплату!" (чек из приложения)
@router.callback_query(F.data.startswith('app_pay_ok:'))
async def app_payment_ok(callback: CallbackQuery, bot):
    request_id = int(callback.data.split(':')[1])

    async with get_db() as session:  # Используем контекстный менеджер

        request = (await session.scalars(select(PaymentRequest).where(PaymentRequest.id_request == request_id).with_for_update())).first()

        if request == None or request.status != 'pending':
            await callback.answer('⚠️ Эту оплату уже обработал другой редактор', show_alert=True)
            await ma.remove_buttons(callback)
            return

        tournament = (await session.scalars(select(Tournament).where(Tournament.tournament_id == request.tournament_id))).first()
        user = (await session.scalars(select(User).where(User.tg_user_id == request.tg_user_id))).first()
        division_names = await get_division_names(session)
        division_name = division_names.get(request.division_level, 'Не определён')

        request.status = 'ok'

        discount = round((tournament.price or 0) - request.price, 1)
        session.add(Payment(id_tournament = tournament.tournament_id, id_tg_user = user.tg_user_id, price = str(request.price), coins = str(discount), photo = request.photo, date = g.now_moscow()))
        session.add(TournamentPlayers(id_tournament = tournament.tournament_id, id_tg_user = user.tg_user_id))

        # Списываем кристаллы
        if request.crystals > 0:
            crystals = get_crystals(user) - request.crystals
            if crystals < 0:
                crystals = 0
            user.coins = crystals
            print(f'✅ Игрок с id {user.tg_user_id} применил {request.crystals} кристаллов для участия в турнире - "{tournament.name_tournament}"!')

        print(f"✅ Игрок с id {user.tg_user_id} зарегистрировался на турнир - '{tournament.name_tournament}' (Mini App)!")

        await callback.answer('✅ Оплата подтверждена')
        await ma.remove_buttons(callback)

    await ma.notify(bot, user.tg_user_id, f"✅ <b>Регистрация на турнир «{escape(tournament.name_tournament)}» подтверждена!</b>\n\n💪 Дивизион: {division_name}\n\nОжидайте завершения регистрации других участников ⚡️", ma.app_keyboard('Мои турниры 🏆', 'tournament'))

    # Добавляем игрока в Google-таблицу турнира (в отдельном потоке, чтобы не тормозить бота)
    try:
        await asyncio.to_thread(gs.addPlayerInList, user.name_user, user.link, tournament.name_tournament, division_name)
        print(f"✅ Игрок добавлен в Excel после регистрации на турнир - '{tournament.name_tournament}' в '{division_name}' дивизион!")
    except Exception as e:
        print(f"Excel не смог добавить пользователя с id {user.tg_user_id} в турнир '{tournament.name_tournament}' и дивизион '{division_name}' из-за ошибки: {e}")
        for editor in EDITOR:
            await ma.notify(bot, editor, f"<b>Не получилось добавить пользователя {escape(user.name_user or '')} в турнир '{escape(tournament.name_tournament)}' в '{division_name}' дивизион из-за ошибки!</b>\n\nОбратитесь в поддержку 🙋‍♂️ @mm_sup")


# Кнопка редактора "❌ Оплата не получена" (чек из приложения)
@router.callback_query(F.data.startswith('app_pay_no:'))
async def app_payment_no(callback: CallbackQuery, bot):
    request_id = int(callback.data.split(':')[1])

    async with get_db() as session:  # Используем контекстный менеджер

        request = (await session.scalars(select(PaymentRequest).where(PaymentRequest.id_request == request_id).with_for_update())).first()

        if request == None or request.status != 'pending':
            await callback.answer('⚠️ Эту оплату уже обработал другой редактор', show_alert=True)
            await ma.remove_buttons(callback)
            return

        request.status = 'rejected'
        tournament = (await session.scalars(select(Tournament).where(Tournament.tournament_id == request.tournament_id))).first()
        editors_list = await f.output_edits_list(session)
        user_id = request.tg_user_id

        await callback.answer('Игрок получит сообщение, что оплата не получена')
        await ma.remove_buttons(callback)

    await ma.notify(bot, user_id, f"😔 <b>Оплата участия в турнире «{escape(tournament.name_tournament)}» не подтверждена</b>\n\nЕсли вы оплатили, свяжитесь с редактором:{editors_list}")
