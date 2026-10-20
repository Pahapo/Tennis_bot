from aiohttp import web

import handlers.gold as g
from webapp.auth import get_tg_user

from config.db_utils import get_db, get_db_readonly
from sqlalchemy import select
from models.User import User
from models.GoldHistory import GoldHistory


# POST /api/visit — заход в приложение: продлевает серию и выдаёт ежедневную награду (1 раз в день)
async def api_visit(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']

    async with get_db() as session:  # Используем контекстный менеджер

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        reward = await g.daily_visit(user_id, session)

    return web.json_response(reward)


# GET /api/gold_history — последние начисления и траты монет
async def api_gold_history(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    async with get_db_readonly() as session:  # Используем контекстный менеджер

        history = (await session.scalars(select(GoldHistory).where(GoldHistory.tg_user_id == tg_user['id']).order_by(GoldHistory.id_history.desc()).limit(20))).all()

        items = []
        for item in history:
            items.append({
                'amount': item.amount,
                'reason': item.reason,
                'comment': item.comment,
                'date': item.date.strftime("%d.%m.%Y")
            })

    return web.json_response(items)


# POST /api/season_seen — игрок посмотрел итоги прошлого года
async def api_season_seen(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']

    async with get_db() as session:  # Используем контекстный менеджер

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        progress = await g.get_progress(user_id, session)
        progress.season_summary_seen = True

    return web.json_response({'ok': True})
