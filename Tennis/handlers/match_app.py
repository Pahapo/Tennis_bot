import asyncio
from html import escape
from datetime import datetime, timedelta
from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, LinkPreviewOptions
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from config.config import WEBAPP_URL, ADMINS, ADMIN_CHAT

import handlers.gold as g

from config.db_utils import get_db
from sqlalchemy import select, func
from models.User import User
from models.Match import Match
from models.MatchReward import MatchReward

# Игры с соперником из Mini App: принятие заявок, счёт, подтверждение по кругу, монеты и планировщик

router = Router()

COURTS = [
    'Северная Америка - Кижеватова 3Б',
    'Африка - Теслы 6',
    'Центральная Европа - Теслы 16',
    'Средиземноморский - Теслы 24',
    'Тропические острова - Лученка 24',
    'Евразия - Лученка 1'
]

MAX_OPEN_REQUESTS = 3          # Сколько заявок на игру может быть у игрока одновременно
SAME_OPPONENT_PER_WEEK = 2     # Монеты за игры с одним соперником — не больше 2 раз в неделю
SAME_OPPONENT_PER_MONTH = 5    # ... и не больше 5 раз в месяц
REJECTS_FOR_ADMINS = 2         # После стольких отклонений счёта пишем админам
SCHEDULER_PAUSE = 300          # Планировщик проверяет игры раз в 5 минут

options = LinkPreviewOptions(is_disabled=True)


# ---------- Вспомогательные функции ----------

def get_match_date(match):  # Дата и время игры
    if match.date_booking:
        return datetime.strptime(match.date_booking, "%H:%M %d.%m.%Y")
    return datetime.strptime(match.date_without_booking, "%H:%M %d.%m.%Y")


def get_players(match):  # ID всех игроков, которые уже в игре
    players = []
    for player in [match.player_1, match.player_2, match.player_3, match.player_4]:
        if player != None:
            players.append(player)
    return players


def is_match_full(match):  # Все места в игре заняты
    if match.type == 'Парный':
        return match.player_4 != None
    return match.player_2 != None


def ids_from_text(text):  # "1,2" -> [1, 2]
    ids = []
    if text:
        for part in text.split(','):
            if part.strip():
                ids.append(int(part))
    return ids


def ids_to_text(ids):  # [1, 2] -> "1,2"
    parts = []
    for user_id in ids:
        parts.append(str(user_id))
    return ','.join(parts)


def check_sets(sets):  # [[6, 4], [3, 6], [7, 5]] -> ("6:4 3:6 7:5", True если выиграла команда 1). None — счёт неверный
    if len(sets) == 0 or len(sets) > 5:
        return None

    parts = []
    wins_1 = 0
    wins_2 = 0

    for one_set in sets:
        if len(one_set) != 2:
            return None

        games_1 = int(one_set[0])
        games_2 = int(one_set[1])

        if games_1 < 0 or games_2 < 0 or games_1 > 99 or games_2 > 99 or games_1 == games_2:
            return None

        if games_1 > games_2:
            wins_1 += 1
        else:
            wins_2 += 1

        parts.append(f"{games_1}:{games_2}")

    if wins_1 == wins_2:
        return None  # Ничьей в теннисе не бывает

    return " ".join(parts), wins_1 > wins_2


def team_1_won(score):  # Кто победил по сохранённому счёту "6:4 3:6 7:5"
    wins_1 = 0
    wins_2 = 0
    for one_set in score.split(' '):
        games_1, games_2 = map(int, one_set.split(':'))
        if games_1 > games_2:
            wins_1 += 1
        else:
            wins_2 += 1
    return wins_1 > wins_2


def get_next_confirmer(match):  # Кто следующий подтверждает счёт (по кругу: игрок 1, 2, 3, 4, кроме автора)
    confirmed = ids_from_text(match.confirmed_by)
    for player in get_players(match):
        if player != match.score_author and player not in confirmed:
            return player
    return None


def app_keyboard(text, screen):  # Кнопка, которая открывает Mini App на нужном экране
    if not WEBAPP_URL:
        return None
    url = WEBAPP_URL.rstrip('/') + '/?screen=' + screen
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))]])


async def get_names(ids, session: AsyncSession):  # Имена игроков через запятую (безопасно для HTML)
    names = []
    for user_id in ids:
        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
        if user and user.name_user:
            names.append(escape(user.name_user))
        else:
            names.append(str(user_id))
    return ', '.join(names)


async def notify(bot, user_id, text, keyboard=None):  # Сообщение игроку (ошибку только печатаем)
    try:
        await bot.send_message(chat_id=user_id, text=text, parse_mode=ParseMode.HTML, link_preview_options=options, reply_markup=keyboard)
    except Exception as e:
        print(f"⚠️ Не удалось отправить сообщение пользователю с id {user_id}: {e}")


async def remove_buttons(callback: CallbackQuery):  # Убираем кнопки под сообщением, чтобы не нажали второй раз
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        print(f"⚠️ Не удалось убрать кнопки: {e}")


async def notify_admins(bot, text):  # Спорный момент — в чат админов (или каждому админу)
    if ADMIN_CHAT:
        await notify(bot, ADMIN_CHAT, text)
    else:
        for admin in ADMINS:
            await notify(bot, admin, text)


async def build_score_text(match, session: AsyncSession):  # Текст со счётом для сообщений
    team_1 = await get_names(ids_from_text(match.team_1), session)
    team_2 = await get_names(ids_from_text(match.team_2), session)
    author = await get_names([match.score_author], session)
    return f"⏰ <b>Игра:</b> {match.date_booking or match.date_without_booking}\n🙋‍♂️ <b>Игроки:</b> {team_1} vs {team_2}\n⚡️ <b>Счёт:</b> {match.score}\n✍️ <b>Записал(-а):</b> {author}"


# ---------- Счёт и подтверждение ----------

async def submit_score(match, author_id, team_1, team_2, score, session: AsyncSession, bot):  # Игрок записал счёт
    match.status = 'confirming'
    match.score = score
    match.team_1 = ids_to_text(team_1)
    match.team_2 = ids_to_text(team_2)
    match.score_author = author_id
    match.score_turn = None
    match.confirmed_by = ''

    await ask_next_confirmation(match, session, bot)


async def ask_next_confirmation(match, session: AsyncSession, bot):  # Отправляем счёт следующему игроку на подтверждение
    next_player = get_next_confirmer(match)

    if next_player == None:
        await finish_match(match, session, bot)  # Все подтвердили
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ Подтвердить', callback_data=f'ms_ok:{match.match_id}'),
                                                      InlineKeyboardButton(text='❌ Не согласен', callback_data=f'ms_no:{match.match_id}')]])

    text = await build_score_text(match, session)
    await notify(bot, next_player, f"<b>Подтвердите счёт игры</b> 🎾\n\n{text}", keyboard)


async def finish_match(match, session: AsyncSession, bot):  # Счёт подтвердили все — начисляем монеты
    match.status = 'done'

    team_1 = ids_from_text(match.team_1)
    team_2 = ids_from_text(match.team_2)
    winner_is_team_1 = team_1_won(match.score)
    game_date = get_match_date(match)

    text = await build_score_text(match, session)

    for player in team_1:
        await reward_player(match, player, team_2, winner_is_team_1, game_date, text, session, bot)

    for player in team_2:
        await reward_player(match, player, team_1, not winner_is_team_1, game_date, text, session, bot)


async def count_rewarded_games(user_id, date_from, date_to, session: AsyncSession, opponent_id=None):  # Сколько засчитанных игр за период
    query = select(func.count()).select_from(MatchReward).where(
        (MatchReward.tg_user_id == user_id) &
        (MatchReward.counted == True) &
        (MatchReward.game_date >= date_from) &
        (MatchReward.game_date < date_to)
    )
    if opponent_id != None:
        query = query.where(MatchReward.opponents.like(f"%,{opponent_id},%"))

    return await session.scalar(query)


async def reward_player(match, user_id, opponents, is_win, game_date, text, session: AsyncSession, bot):  # Монеты одному игроку за игру
    # Неделя — с понедельника, месяц — календарный
    week_start = (game_date - timedelta(days=game_date.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    month_start = game_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if month_start.month == 12:
        month_end = month_start.replace(year=month_start.year + 1, month=1)
    else:
        month_end = month_start.replace(month=month_start.month + 1)

    games_this_week = await count_rewarded_games(user_id, week_start, week_end, session)

    # Лимит игр с одним и тем же соперником
    limited = False
    for opponent_id in opponents:
        week_with_opponent = await count_rewarded_games(user_id, week_start, week_end, session, opponent_id)
        month_with_opponent = await count_rewarded_games(user_id, month_start, month_end, session, opponent_id)
        if week_with_opponent >= SAME_OPPONENT_PER_WEEK or month_with_opponent >= SAME_OPPONENT_PER_MONTH:
            limited = True

    user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
    is_banned = user.ban_status == True

    progress = await g.get_progress(user_id, session)
    league = g.get_league(progress.season_gold)

    amount = 0
    if not limited:
        amount = g.match_reward(league, is_win, games_this_week, is_banned)

    session.add(MatchReward(match_id = match.match_id, tg_user_id = user_id, opponents = ',' + ids_to_text(opponents) + ',', is_win = is_win, amount = amount, counted = not limited, game_date = game_date))

    if is_win:
        result = 'Победа'
        reason = 'match_win'
    else:
        result = 'Поражение'
        reason = 'match_loss'

    opponent_names = await get_names(opponents, session)
    await g.add_gold(user_id, amount, reason, session, comment = f"{result} {match.score} vs {opponent_names}"[:100])

    # Сообщение игроку
    if limited:
        reward_text = f"🪙 Монет нет: с этим соперником уже сыграно {SAME_OPPONENT_PER_WEEK} игры за неделю или {SAME_OPPONENT_PER_MONTH} за месяц"
    elif games_this_week >= g.FULL_GAMES_PER_WEEK:
        reward_text = f"🪙 +{amount} (с 4-й игры за неделю монет в 5 раз меньше)"
    else:
        reward_text = f"🪙 +{amount}"

    await notify(bot, user_id, f"✅ <b>Счёт подтверждён! {result}</b>\n\n{text}\n\n{reward_text}", app_keyboard('Открыть лиги 🏆', 'arena'))


# Кнопка "✅ Подтвердить" под счётом
@router.callback_query(F.data.startswith('ms_ok:'))
async def match_score_ok(callback: CallbackQuery, bot):
    match_id = int(callback.data.split(':')[1])
    user_id = callback.from_user.id

    async with get_db() as session:  # Используем контекстный менеджер

        match = (await session.scalars(select(Match).where(Match.match_id == match_id).with_for_update())).first()

        if match == None or match.status != 'confirming' or get_next_confirmer(match) != user_id:
            await callback.answer('Этот счёт уже неактуален', show_alert=True)
            await remove_buttons(callback)
            return

        confirmed = ids_from_text(match.confirmed_by)
        confirmed.append(user_id)
        match.confirmed_by = ids_to_text(confirmed)

        await callback.answer('✅ Счёт подтверждён!')
        await remove_buttons(callback)

        await ask_next_confirmation(match, session, bot)


# Кнопка "❌ Не согласен" под счётом — игрок сам вводит свой счёт в приложении
@router.callback_query(F.data.startswith('ms_no:'))
async def match_score_no(callback: CallbackQuery, bot):
    match_id = int(callback.data.split(':')[1])
    user_id = callback.from_user.id

    async with get_db() as session:  # Используем контекстный менеджер

        match = (await session.scalars(select(Match).where(Match.match_id == match_id).with_for_update())).first()

        if match == None or match.status != 'confirming' or get_next_confirmer(match) != user_id:
            await callback.answer('Этот счёт уже неактуален', show_alert=True)
            await remove_buttons(callback)
            return

        text = await build_score_text(match, session)
        user_name = await get_names([user_id], session)
        author_id = match.score_author

        match.status = 'wait_score'
        match.score_turn = user_id  # Теперь счёт вводит только тот, кто не согласен
        match.reject_count = (match.reject_count or 0) + 1

        await callback.answer('Введите свой счёт в приложении')
        await remove_buttons(callback)

        await notify(bot, user_id, "<b>Вы не согласны со счётом</b> 😥\n\nВведите правильный счёт — он уйдёт сопернику на подтверждение 👇", app_keyboard('Записать счёт 🎾', 'score'))
        await notify(bot, author_id, f"<b>{user_name} не согласен(-на) со счётом</b> 😥\n\n{text}\n\nСоперник введёт свой счёт, и он придёт вам на подтверждение")

        if match.reject_count == REJECTS_FOR_ADMINS:
            await notify_admins(bot, f"❗️ <b>Спорный момент в игре с соперником</b> (ID игры: {match.match_id})\n\nСчёт отклонили {match.reject_count} раза\n\n{text}\n\n<b>Последним не согласился:</b> {user_name}")


# ---------- Заявки на игру ----------

# Кнопка "✅ Принять" у создателя игры
@router.callback_query(F.data.startswith('ma_yes:'))
async def match_accept(callback: CallbackQuery, bot):
    parts = callback.data.split(':')
    match_id = int(parts[1])
    applicant_id = int(parts[2])

    async with get_db() as session:  # Используем контекстный менеджер

        match = (await session.scalars(select(Match).where(Match.match_id == match_id).with_for_update())).first()

        if match == None or match.id_tg_user != callback.from_user.id or match.status != None:
            await callback.answer('Игра не найдена или уже прошла', show_alert=True)
            await remove_buttons(callback)
            return

        if is_match_full(match):
            await callback.answer('В игре уже нет свободных мест', show_alert=True)
            await remove_buttons(callback)
            return

        if applicant_id in get_players(match):
            await callback.answer('Этот игрок уже в игре', show_alert=True)
            await remove_buttons(callback)
            return

        if match.player_2 == None:
            match.player_2 = applicant_id
        elif match.player_3 == None:
            match.player_3 = applicant_id
        else:
            match.player_4 = applicant_id

        date = match.date_booking or match.date_without_booking
        creator_name = await get_names([match.id_tg_user], session)
        applicant_name = await get_names([applicant_id], session)

        await callback.answer('✅ Игрок добавлен в игру!')
        await remove_buttons(callback)

        if is_match_full(match):
            await callback.message.answer(f"✅ <b>Игра объявлена!</b>\n\n⏰ {date}\n🙋‍♂️ Игроки: {await get_names(get_players(match), session)}\n\nНапомню за 2 часа до начала ⚡️", parse_mode=ParseMode.HTML, link_preview_options=options)
        else:
            await callback.message.answer(f"✅ <b>{applicant_name} в игре!</b> Ждём остальных игроков ⏳", parse_mode=ParseMode.HTML)

        await notify(bot, applicant_id, f"✅ <b>{creator_name} принял(-а) вашу заявку!</b>\n\n⏰ Игра: {date}\n\nНапомню за 2 часа до начала ⚡️", app_keyboard('Мои игры 🎾', 'opponent'))


# Кнопка "❌ Отклонить" у создателя игры
@router.callback_query(F.data.startswith('ma_no:'))
async def match_reject(callback: CallbackQuery, bot):
    parts = callback.data.split(':')
    match_id = int(parts[1])
    applicant_id = int(parts[2])

    async with get_db() as session:  # Используем контекстный менеджер
        match = (await session.scalars(select(Match).where(Match.match_id == match_id))).first()
        creator_name = await get_names([callback.from_user.id], session)

    await callback.answer('Заявка отклонена')
    await remove_buttons(callback)

    if match and match.id_tg_user == callback.from_user.id:
        date = match.date_booking or match.date_without_booking
        await notify(bot, applicant_id, f"😥 <b>{creator_name} отклонил(-а) вашу заявку</b> на игру {date}\n\nПопробуйте найти другую игру 👇", app_keyboard('Найти игру 🎾', 'opponent'))


# ---------- Планировщик ----------

async def check_matches(bot):  # Напоминание за 2 часа и запрос счёта через 2 часа после начала
    now = g.now_moscow()

    async with get_db() as session:  # Используем контекстный менеджер

        matches = (await session.scalars(select(Match).where(Match.status == None))).all()

        for match in matches:
            try:
                match_date = get_match_date(match)
            except (ValueError, TypeError):
                continue

            # Никто не откликнулся, а время прошло — удаляем, как и раньше
            if not is_match_full(match):
                if match_date < now:
                    await session.delete(match)
                continue

            # Очень старые игры (например, с прошлого сезона) — тоже удаляем, счёт по ним уже не спросить
            if now - match_date > timedelta(days=3):
                await session.delete(match)
                continue

            date = match.date_booking or match.date_without_booking

            if match.reminder_sent != True and match_date - timedelta(hours=2) <= now < match_date:
                match.reminder_sent = True
                names = await get_names(get_players(match), session)
                for player in get_players(match):
                    await notify(bot, player, f"⏰ <b>Напоминание!</b>\n\n⚡️ Через 2 часа игра ({date})\n🙋‍♂️ Игроки: {names}")

            if now >= match_date + timedelta(hours=2):
                match.status = 'wait_score'
                await notify(bot, match.player_1, f"🎾 <b>Как прошла игра {date}?</b>\n\nЗапишите счёт — после подтверждения соперником все получат монеты 🪙", app_keyboard('Записать счёт 🎾', 'score'))


async def match_scheduler(bot):  # Запускается в main.py
    while True:
        try:
            await check_matches(bot)
        except Exception as e:
            print(f"⚠️ Ошибка в планировщике игр: {e}")
        await asyncio.sleep(SCHEDULER_PAUSE)
