from aiohttp import web

import handlers.achievements as ach
from webapp.auth import get_tg_user
from webapp.api_match import read_json

from config.db_utils import get_db
from sqlalchemy import select
from models.User import User


# GET /api/achievements — все достижения игрока по группам (для профиля)
async def api_achievements(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    async with get_db() as session:  # get_db: прогресс игрока может создаться при первом заходе

        user = (await session.scalars(select(User).where(User.tg_user_id == tg_user['id']))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        result = await ach.get_list(user.tg_user_id, session)

    return web.json_response(result)


# POST /api/achievements/seen — игрок нажал "Понятно!" в окне достижения: {id}
async def api_achievements_seen(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    data = await read_json(request)

    async with get_db() as session:  # Используем контекстный менеджер
        await ach.mark_seen(tg_user['id'], str(data.get('id') or ''), session)

    return web.json_response({'ok': True})
