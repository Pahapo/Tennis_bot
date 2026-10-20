import pytz
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from models.PlayerProgress import PlayerProgress
from models.GoldHistory import GoldHistory

# Монеты 🪙 — награды за активность (матчи, рефералы, заходы). По монетам за год считается лига.
# Кристаллы 💎 — это старые монеты бота (users.coins), их логика не меняется.

MOSCOW_TZ = pytz.timezone("Europe/Moscow")

# Лиги: название и сколько монет нужно заработать с начала года
LEAGUES = [
    {'name': 'Дворовый корт', 'from': 0},
    {'name': 'Школьная площадка', 'from': 80},
    {'name': 'Парковый корт', 'from': 200},
    {'name': 'Грунтовый клуб', 'from': 370},
    {'name': 'Городская арена', 'from': 600},
    {'name': 'Травяной клуб', 'from': 900},
    {'name': 'Ночной стадион', 'from': 1250},
    {'name': 'Крытый дворец', 'from': 1650},
    {'name': 'Арена чемпионов', 'from': 2150},
    {'name': 'Центральный корт', 'from': 2750}
]

# Монеты за матч по лигам (индекс 0 — лига 1)
WIN_GOLD = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65]
LOSS_GOLD = [4, 4, 5, 6, 7, 8, 9, 9, 10, 11]
FULL_GAMES_PER_WEEK = 3    # Столько игр в неделю дают полные монеты, дальше — в 5 раз меньше
BANNED_DIVIDER = 5         # Игроки с баном получают за игру в 5 раз меньше

# Ежедневная награда за заход в приложение и бонусы за серию
DAILY_GOLD = 1
STREAK_BONUS = {7: 5, 30: 15, 100: 40, 200: 60, 365: 100}

REFERRAL_GOLD = 100        # Один раз за каждого приглашённого друга


def now_moscow():
    return datetime.now(MOSCOW_TZ).replace(tzinfo=None)


def get_league(season_gold):  # Номер лиги (1-10) по монетам, заработанным за год
    league = 1
    for i in range(len(LEAGUES)):
        if season_gold >= LEAGUES[i]['from']:
            league = i + 1
    return league


def match_reward(league, is_win, games_this_week, is_banned):  # Сколько монет дать за матч
    if is_win:
        amount = WIN_GOLD[league - 1]
    else:
        amount = LOSS_GOLD[league - 1]

    # games_this_week — сколько игр уже засчитано на этой неделе (без текущей)
    if games_this_week >= FULL_GAMES_PER_WEEK:
        amount = int(amount / 5)

    if is_banned:
        amount = int(amount / BANNED_DIVIDER)

    return amount


async def get_progress(user_id, session: AsyncSession):  # Прогресс игрока (создаётся при первом обращении)
    # with_for_update — блокируем строку, чтобы два одновременных запроса не начислили монеты дважды
    progress = (await session.scalars(select(PlayerProgress).where(PlayerProgress.tg_user_id == user_id).with_for_update())).first()
    year = now_moscow().year

    if progress == None:
        progress = PlayerProgress(tg_user_id = user_id, season_year = year)
        session.add(progress)
        await session.flush()
        return progress

    # Наступил новый год — лига обнуляется, баланс монет остаётся
    if progress.season_year != year:
        if progress.season_gold > 0:
            progress.last_season_gold = progress.season_gold
            progress.season_summary_seen = False
        progress.season_gold = 0
        progress.season_year = year

    return progress


async def add_gold(user_id, amount, reason, session: AsyncSession, comment=None):  # Начисление монет
    if amount <= 0:
        return

    progress = await get_progress(user_id, session)
    progress.gold += amount
    progress.season_gold += amount

    session.add(GoldHistory(tg_user_id = user_id, amount = amount, reason = reason, date = now_moscow(), comment = comment))


async def spend_gold(user_id, amount, reason, session: AsyncSession, comment=None):  # Трата монет. False — если монет не хватает
    progress = await get_progress(user_id, session)

    if progress.gold < amount:
        return False  # В минус уйти нельзя

    progress.gold -= amount  # Лига не меняется: season_gold не трогаем

    session.add(GoldHistory(tg_user_id = user_id, amount = -amount, reason = reason, date = now_moscow(), comment = comment))
    return True


async def daily_visit(user_id, session: AsyncSession):  # Заход в приложение: серия и ежедневная награда
    progress = await get_progress(user_id, session)
    today = now_moscow().date()

    if progress.last_visit == today:
        return {'gold': 0, 'bonus': 0, 'streak': progress.streak_days}  # Сегодня уже получал

    if progress.last_visit == today - timedelta(days=1):
        progress.streak_days += 1  # Заходил вчера — серия продолжается
    else:
        progress.streak_days = 1   # Пропустил день — серия начинается заново

    progress.last_visit = today

    if progress.streak_days > progress.best_streak:
        progress.best_streak = progress.streak_days

    await add_gold(user_id, DAILY_GOLD, 'daily', session, comment = f"Ежедневная награда, день {progress.streak_days}")

    bonus = 0
    if progress.streak_days in STREAK_BONUS:
        bonus = STREAK_BONUS[progress.streak_days]
        await add_gold(user_id, bonus, 'streak', session, comment = f"Серия {progress.streak_days} дней подряд")

    return {'gold': DAILY_GOLD, 'bonus': bonus, 'streak': progress.streak_days}
