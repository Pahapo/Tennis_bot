import os
from aiohttp import web

import handlers.referrals as r
import handlers.gold as g
import handlers.skins as sk
import handlers.achievements as ach
from webapp.auth import get_tg_user
from webapp.api_news import count_unread_news

from config.db_utils import get_db
from sqlalchemy import select
from models.User import User
from models.Division import Division
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers
from models.Referrals import Referrals
from models.PendingReferral import PendingReferral


# Картинки лиг: leagueN (корт лиги) и fN (обложка-фон лиги) в формате webp, png или jpg.
# Если картинки leagueN нет — берём нарисованную N.svg, если нет fN — обложки не будет
LOCATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'webapp_static', 'img', 'locations')
IMAGE_TYPES = ['webp', 'png', 'jpg', 'jpeg']


def find_location_image(name):  # Ссылка на картинку name.webp / .png / .jpg или None
    for image_type in IMAGE_TYPES:
        if os.path.exists(os.path.join(LOCATIONS_DIR, f'{name}.{image_type}')):
            return f'/static/img/locations/{name}.{image_type}'
    return None


def print_league_images():  # При запуске пишем в консоль, какие картинки лиг найдены
    found = []
    missing = []
    for i in range(len(g.LEAGUES)):
        number = i + 1
        for prefix in ['league', 'f']:
            if find_location_image(f'{prefix}{number}'):
                found.append(f'{prefix}{number}')
            else:
                missing.append(f'{prefix}{number}')

    print(f"🖼 Картинки лиг в {LOCATIONS_DIR}")
    print(f"   найдены: {', '.join(found) or 'нет'}")
    print(f"   нет (будет старая картинка или без обложки): {', '.join(missing) or 'все на месте'}")


def leagues_with_images():  # Лиги для фронта: название, порог, картинка и обложка
    result = []
    for i in range(len(g.LEAGUES)):
        number = i + 1

        image = find_location_image(f'league{number}')
        if image == None:
            image = f'/static/img/locations/{number}.svg'

        cover = find_location_image(f'f{number}')

        result.append({'name': g.LEAGUES[i]['name'], 'from': g.LEAGUES[i]['from'], 'image': image, 'cover': cover})
    return result


# GET /api/me — данные профиля игрока
async def api_me(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']

    async with get_db() as session:  # get_db, а не readonly: прогресс игрока может создаться при первом заходе

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        # Дивизион
        division_name = 'Не определён'
        if user.division_level != None:
            division = (await session.scalars(select(Division).where(Division.division_id == user.division_level))).first()
            if division:
                division_name = division.name_division

        # История турниров
        user_in_tournaments = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tg_user == user_id))).all()
        tournament_ids = [games.id_tournament for games in user_in_tournaments]

        tournaments = []
        if tournament_ids:
            history_tournaments = (await session.scalars(select(Tournament).where(Tournament.tournament_id.in_(tournament_ids)))).all()
            for tournament in history_tournaments:
                tournaments.append(tournament.name_tournament)

        # Рефералы
        user_referrals = (await session.scalars(select(Referrals).where(Referrals.tg_users_id == user_id))).first()

        friends = 0
        if user_referrals and user_referrals.count:
            friends = user_referrals.count

        # Сколько приглашённых уже сыграли первую игру (за них пришла награда)
        friends_played = len((await session.scalars(select(PendingReferral).where((PendingReferral.referrer_id == user_id) & (PendingReferral.rewarded == True)))).all())

        # Монеты, лига и серия
        progress = await g.get_progress(user_id, session)

        # Новые достижения: выдаём при каждом открытии приложения и после действий в нём
        await ach.check_achievements(user_id, session)
        new_achievements = await ach.get_unseen(user_id, session)

        # Ежедневную награду игрок забирает сам — кнопкой на главном экране
        daily_available = progress.last_visit != g.now_moscow().date()

        unread_news = await count_unread_news(user, progress.last_news_seen, session)

        season_summary = None
        if progress.season_summary_seen == False:
            season_summary = {
                'year': progress.season_year - 1,
                'gold': progress.last_season_gold,
                'league': g.get_league(progress.last_season_gold)
            }

    # Кристаллы — это монеты, которые уже есть в боте (users.coins)
    crystals = 0
    if user.coins:
        crystals = int(user.coins)

    ban_until = None
    if user.ban_status == True:
        ban_until = user.end_date_ban

    return web.json_response({
        'name': user.name_user,
        'link': user.link,
        'age': user.age,
        'sex': user.sex,
        'division': division_name,
        'rating': user.rating,
        'crystals': crystals,
        'ban_until': ban_until,
        'tournaments': tournaments,
        'referral_link': await r.generate_referral_link(user_id),
        'friends': friends,
        'friends_played': friends_played,
        'referral_gold': g.REFERRAL_GOLD,
        'referral_crystals': r.REFERRAL_CRYSTALS,
        'gold': progress.gold,
        'season_gold': progress.season_gold,
        'league': g.get_league(progress.season_gold),
        'leagues': leagues_with_images(),
        'streak': progress.streak_days,
        'best_streak': progress.best_streak,
        'season_summary': season_summary,
        'daily_available': daily_available,
        'unread_news': unread_news,
        'hero': sk.get_hero(progress),
        'background': sk.get_background(progress),
        'racket': sk.get_racket(progress),
        'new_achievements': new_achievements
    })
