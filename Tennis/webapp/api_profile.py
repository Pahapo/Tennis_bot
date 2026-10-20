from aiohttp import web

import handlers.referrals as r
import handlers.gold as g
from webapp.auth import get_tg_user

from config.db_utils import get_db
from sqlalchemy import select
from models.User import User
from models.Division import Division
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers
from models.Referrals import Referrals


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

        # Монеты, лига и серия
        progress = await g.get_progress(user_id, session)

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
        'gold': progress.gold,
        'season_gold': progress.season_gold,
        'league': g.get_league(progress.season_gold),
        'leagues': g.LEAGUES,
        'streak': progress.streak_days,
        'best_streak': progress.best_streak,
        'season_summary': season_summary
    })
