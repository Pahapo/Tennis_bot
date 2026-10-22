from sqlalchemy.ext.asyncio import AsyncSession

import handlers.gold as g
import handlers.skins as sk
import handlers.tournament_app as ta

from sqlalchemy import select, func
from models.Achievement import Achievement
from models.News import News
from models.Match import Match
from models.PlayerSkin import PlayerSkin
from models.PlayerProgress import PlayerProgress
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers
from models.User import User

# Достижения игрока. Проверяются при каждом открытии приложения (GET /api/me) и после действий в нём.
# Новое достижение: окно с поздравлением в приложении + личная новость в разделе "Новости".
#
# stat — какую цифру игрока сравниваем (см. get_stats), need — сколько нужно

GROUPS = [
    {'id': 'games', 'name': '🎾 Игры с соперником'},
    {'id': 'tournaments', 'name': '🏆 Турниры'},
    {'id': 'streak', 'name': '🔥 Дни подряд в приложении'},
    {'id': 'leagues', 'name': '🏅 Лиги'},
    {'id': 'skins', 'name': '🛍 Коллекция скинов'}
]


def count_skins(skin_type):  # Сколько всего скинов этого типа в магазине
    count = 0
    for skin in sk.SKINS:
        if skin['type'] == skin_type:
            count += 1
    return count


ACHIEVEMENTS = []

# --- Игры с соперником (счёт подтвердили все участники) ---
GAMES = [
    (1, 'Первая подача', 'Сыграна первая игра с соперником', 'Вот это начало! Первая игра позади — корт официально узнал твоё имя. Дальше будет только интереснее 🎾'),
    (5, 'Разогрев', 'Сыграно 5 игр с соперником', 'Пять игр — и ты уже в ритме! Рука набита, азарт растёт. Так держать 💪'),
    (20, 'Завсегдатай корта', 'Сыграно 20 игр с соперником', 'Двадцать игр! Тебя уже узнают на корте и зовут на матч. Ты — часть теннисной жизни Минск Мира 🔥'),
    (50, 'Ветеран корта', 'Сыграно 50 игр с соперником', 'Полсотни игр — это уровень ветерана! Опыт, выдержка и характер — всё при тебе 🏅'),
    (100, 'Легенда корта', 'Сыграно 100 игр с соперником', 'Сто игр! Это легендарно. О таких игроках рассказывают новичкам. Ты — легенда корта 👑')
]
for need, title, done, praise in GAMES:
    ACHIEVEMENTS.append({'id': f'games_{need}', 'group': 'games', 'icon': '🎾', 'title': title, 'goal': f'Сыграть {need} игр с соперником' if need > 1 else 'Сыграть первую игру с соперником',
                         'done': done, 'praise': praise, 'stat': 'games', 'need': need})

# --- Турниры (засчитываются, когда наступила дата окончания турнира) ---
TOURNAMENTS = [
    (1, 'Первый турнир', 'Сыгран первый турнир', 'Первый турнир за плечами! Ты вышел(-шла) на большую сцену и справился(-ась). Это только начало турнирного пути 🏆'),
    (3, 'Турнирный боец', 'Сыграно 3 турнира', 'Три турнира! Ты уже настоящий турнирный боец — соперники знают, что с тобой будет непросто ⚔️'),
    (10, 'Турнирный чемпион', 'Сыграно 10 турниров', 'Десять турниров! Это путь чемпиона. Твоё имя навсегда вписано в историю клуба 👑')
]
for need, title, done, praise in TOURNAMENTS:
    ACHIEVEMENTS.append({'id': f'tournaments_{need}', 'group': 'tournaments', 'icon': '🏆', 'title': title, 'goal': f'Сыграть {need} турниров' if need > 1 else 'Сыграть первый турнир',
                         'done': done, 'praise': praise, 'stat': 'tournaments', 'need': need})

# --- Дни подряд в приложении (лучшая серия ежедневных наград) ---
STREAK = [
    (1, 'Первый шаг', 'Первый день в приложении', 'Добро пожаловать в игру! Первый сундук открыт — каждый день здесь тебя ждёт что-то новое 🎁'),
    (3, 'Три дня в игре', '3 дня подряд в приложении', 'Три дня подряд — привычка начинает формироваться! Ты на верном пути 🔥'),
    (7, 'Неделя без пропусков', '7 дней подряд в приложении', 'Целая неделя без пропусков! Такая дисциплина — признак настоящего спортсмена 💪'),
    (14, 'Две недели огня', '14 дней подряд в приложении', 'Две недели подряд! Твоя серия горит ярче прожекторов на центральном корте 🔥'),
    (30, 'Месяц дисциплины', '30 дней подряд в приложении', 'Месяц без единого пропуска! Это уже не привычка — это характер чемпиона 🏅'),
    (50, 'Полсотни дней', '50 дней подряд в приложении', 'Пятьдесят дней подряд! Такой преданности теннису можно только позавидовать 🌟'),
    (100, 'Сотня!', '100 дней подряд в приложении', 'Сто дней подряд! Невероятная сила воли — ты вдохновляешь весь клуб 🚀'),
    (200, '200 дней силы', '200 дней подряд в приложении', 'Двести дней подряд! Это уровень, до которого доходят единицы. Снимаем шляпу 🎩'),
    (365, 'Целый год!', '365 дней подряд в приложении', 'Целый год каждый день! Это абсолютная легенда. Клуб гордится тобой 👑')
]
for need, title, done, praise in STREAK:
    ACHIEVEMENTS.append({'id': f'streak_{need}', 'group': 'streak', 'icon': '🔥', 'title': title, 'goal': f'Заходить в приложение {need} дней подряд' if need > 1 else 'Забрать первую ежедневную награду',
                         'done': done, 'praise': praise, 'stat': 'streak', 'need': need})

# --- Лиги (достиг лиги хотя бы раз; лиги обнуляются 31 декабря, достижение остаётся) ---
for i in range(len(g.LEAGUES)):
    number = i + 1
    name = g.LEAGUES[i]['name']
    praise = f'Ты достиг(-ла) лиги «{name}»! Новая локация открыта — здесь соперники сильнее, а победы слаще 🏅'
    if number == 1:
        praise = f'Добро пожаловать на «{name}»! Здесь начинается путь каждого чемпиона — впереди ещё 9 лиг 🏅'
    ACHIEVEMENTS.append({'id': f'league_{number}', 'group': 'leagues', 'icon': '🏅', 'title': f'Лига {number}: {name}', 'goal': f'Достичь лиги «{name}»',
                         'done': f'Достигнута лига «{name}»', 'praise': praise, 'stat': 'league', 'need': number})

# --- Коллекция скинов (бесплатные герой и ракетка тоже считаются) ---
ACHIEVEMENTS.append({'id': 'skins_first', 'group': 'skins', 'icon': '🛍', 'title': 'Первая покупка', 'goal': 'Купить первый скин в магазине',
                     'done': 'Куплен первый скин', 'praise': 'Отличный вкус! Твой первый скин уже сияет на корте — теперь соперники точно тебя запомнят ✨',
                     'stat': 'skins_bought', 'need': 1})
ACHIEVEMENTS.append({'id': 'skins_all_hero', 'group': 'skins', 'icon': '🦸', 'title': 'Вся команда героев', 'goal': 'Собрать всех героев',
                     'done': 'Собраны все герои', 'praise': 'Невероятно! У тебя собраны все герои — настоящая звёздная команда в одних руках 🌟',
                     'stat': 'hero_owned', 'need': count_skins('hero')})
ACHIEVEMENTS.append({'id': 'skins_all_background', 'group': 'skins', 'icon': '🖼', 'title': 'Коллекционер арен', 'goal': 'Собрать все фоны',
                     'done': 'Собраны все фоны', 'praise': 'Все арены мира теперь твои! Выбирай любую — ты везде как дома 🌍',
                     'stat': 'background_owned', 'need': count_skins('background')})
ACHIEVEMENTS.append({'id': 'skins_all_racket', 'group': 'skins', 'icon': '🎾', 'title': 'Оружейная мастера', 'goal': 'Собрать все ракетки',
                     'done': 'Собраны все ракетки', 'praise': 'Полная оружейная! С такой коллекцией ракеток ты готов(-а) к любому сопернику 💪',
                     'stat': 'racket_owned', 'need': count_skins('racket')})
ACHIEVEMENTS.append({'id': 'skins_all', 'group': 'skins', 'icon': '👑', 'title': 'Великий коллекционер', 'goal': 'Собрать все скины',
                     'done': 'Собраны все скины', 'praise': 'Это легендарно! Ты собрал(-а) абсолютно все скины — такого коллекционера клуб ещё не видел 👑',
                     'stat': 'skins_owned', 'need': len(sk.SKINS)})


def find_achievement(achievement_id):  # Достижение по id (или None)
    for achievement in ACHIEVEMENTS:
        if achievement['id'] == achievement_id:
            return achievement
    return None


async def count_games(user_id, session: AsyncSession):  # Игры с соперником, по которым все подтвердили счёт
    games = (await session.scalars(select(Match).where((Match.status == 'done') & (
        (Match.player_1 == user_id) | (Match.player_2 == user_id) | (Match.player_3 == user_id) | (Match.player_4 == user_id)
    )))).all()
    return len(games)


async def count_tournaments(user_id, session: AsyncSession):  # Турниры игрока, у которых наступила дата окончания
    rows = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == user_id))).all()
    tournament_ids = []
    for row in rows:
        if row.id_tournament not in tournament_ids:
            tournament_ids.append(row.id_tournament)

    if not tournament_ids:
        return 0

    today = g.now_moscow().replace(hour=0, minute=0, second=0, microsecond=0)
    count = 0
    for tournament in (await session.scalars(select(Tournament).where(Tournament.tournament_id.in_(tournament_ids)))).all():
        end = ta.parse_day(tournament.end_tournament)
        if end != None and end <= today:
            count += 1
    return count


async def get_stats(user_id, session: AsyncSession):  # Все цифры игрока, по которым считаются достижения
    progress = await g.get_progress(user_id, session)
    owned = await sk.get_owned_skins(user_id, session)
    bought = (await session.scalars(select(PlayerSkin).where(PlayerSkin.tg_user_id == user_id))).all()

    # Лига: текущая или прошлогодняя (если лиги уже обнулились, а достижение ещё не выдано)
    league = g.get_league(progress.season_gold)
    if progress.last_season_gold and g.get_league(progress.last_season_gold) > league:
        league = g.get_league(progress.last_season_gold)

    stats = {
        'games': await count_games(user_id, session),
        'tournaments': await count_tournaments(user_id, session),
        'streak': max(progress.best_streak, progress.streak_days),
        'league': league,
        'skins_bought': len(bought),
        'hero_owned': 0,
        'background_owned': 0,
        'racket_owned': 0,
        'skins_owned': 0
    }

    for skin in sk.SKINS:
        if skin['id'] in owned:
            stats[skin['type'] + '_owned'] += 1
            stats['skins_owned'] += 1

    return stats


async def check_achievements(user_id, session: AsyncSession):  # Выдать новые достижения (окно + личная новость)
    stats = await get_stats(user_id, session)

    have = []
    for row in (await session.scalars(select(Achievement).where(Achievement.tg_user_id == user_id))).all():
        have.append(row.achievement)

    now = g.now_moscow()
    for achievement in ACHIEVEMENTS:
        if achievement['id'] in have:
            continue
        if stats[achievement['stat']] < achievement['need']:
            continue

        session.add(Achievement(tg_user_id = user_id, achievement = achievement['id'], date = now))
        session.add(News(date = now, tg_user_id = user_id, text = f"{achievement['icon']} Новое достижение «{achievement['title']}»\n{achievement['done']}"))
        print(f"🏅 Игрок {user_id} получил достижение {achievement['id']}")

    await session.flush()


async def league_percents(session: AsyncSession):  # Какой % зарегистрированных игроков достиг каждой лиги
    total = (await session.scalar(select(func.count(User.tg_user_id)))) or 0

    reached = []
    for i in range(len(g.LEAGUES)):
        reached.append([])

    # Кто получил достижение лиги
    for row in (await session.scalars(select(Achievement).where(Achievement.achievement.like('league_%')))).all():
        number = int(row.achievement.split('_')[1])
        if row.tg_user_id not in reached[number - 1]:
            reached[number - 1].append(row.tg_user_id)

    # ... и кто сейчас в этой лиге или выше (даже если ещё не открывал приложение)
    for progress in (await session.scalars(select(PlayerProgress))).all():
        league = g.get_league(progress.season_gold)
        for number in range(1, league + 1):
            if progress.tg_user_id not in reached[number - 1]:
                reached[number - 1].append(progress.tg_user_id)

    # В 1-й лиге с 0 монет начинает каждый зарегистрированный игрок
    percents = []
    for users in reached:
        if len(percents) == 0:
            percents.append(100 if total > 0 else 0)
            continue
        if total == 0:
            percents.append(0)
            continue
        percent = round(len(users) / total * 100)
        if percent == 0 and len(users) > 0:
            percent = 1  # Меньше 1% показываем как 1%
        percents.append(min(percent, 100))
    return percents


def window_data(achievement, percents):  # Данные для окна с поздравлением
    data = {
        'id': achievement['id'],
        'icon': achievement['icon'],
        'title': achievement['title'],
        'praise': achievement['praise'],
        'percent': None
    }
    if achievement['group'] == 'leagues':
        data['percent'] = percents[achievement['need'] - 1]
    return data


async def get_unseen(user_id, session: AsyncSession):  # Новые достижения, окно о которых игрок ещё не видел
    rows = (await session.scalars(select(Achievement).where((Achievement.tg_user_id == user_id) & (Achievement.seen == False)).order_by(Achievement.id_achievement))).all()
    if not rows:
        return []

    percents = await league_percents(session)
    result = []
    for row in rows:
        achievement = find_achievement(row.achievement)
        if achievement:
            result.append(window_data(achievement, percents))
    return result


async def mark_seen(user_id, achievement_id, session: AsyncSession):  # Игрок нажал "Понятно!"
    row = (await session.scalars(select(Achievement).where((Achievement.tg_user_id == user_id) & (Achievement.achievement == achievement_id)))).first()
    if row:
        row.seen = True


def progress_text(achievement, stats):  # "12 / 20" — сколько уже сделано
    value = stats[achievement['stat']]
    if achievement['group'] == 'leagues':
        return ''  # У лиг прогресс не пишем — текущая лига видна на главном экране
    if achievement['group'] == 'streak':
        return f'{min(value, achievement["need"])} / {achievement["need"]} дн.'
    return f'{min(value, achievement["need"])} / {achievement["need"]}'


async def get_list(user_id, session: AsyncSession):  # Все достижения по группам для профиля
    stats = await get_stats(user_id, session)

    dates = {}
    for row in (await session.scalars(select(Achievement).where(Achievement.tg_user_id == user_id))).all():
        dates[row.achievement] = row.date.strftime("%d.%m.%Y")

    groups = []
    for group in GROUPS:
        items = []
        for achievement in ACHIEVEMENTS:
            if achievement['group'] != group['id']:
                continue

            item = {
                'id': achievement['id'],
                'icon': achievement['icon'],
                'title': achievement['title'],
                'goal': achievement['goal'],
                'earned': achievement['id'] in dates,
                'date': dates.get(achievement['id']),
                'progress': progress_text(achievement, stats)
            }
            items.append(item)

        groups.append({'name': group['name'], 'items': items})

    earned = len(dates)
    return {'groups': groups, 'earned': earned, 'total': len(ACHIEVEMENTS)}
