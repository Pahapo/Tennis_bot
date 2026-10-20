from aiohttp import web

import handlers.validation as valid
from webapp.auth import get_tg_user
from webapp.api_match import read_json

from config.db_utils import get_db
from sqlalchemy import select
from models.User import User
from models.OldUsers import OldUsers


# POST /api/register — регистрация нового игрока из приложения: {name, skill}
# То же, что раньше делал бот в чате (handlers/functions.py: save_user, register_name, register_skill)
async def api_register(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']
    data = await read_json(request)

    name = str(data.get('name') or '').strip()
    skill = str(data.get('skill') or '').strip()

    if name == '' or not valid.validate_name(name) or not valid.validate_start(name):
        return web.json_response({'error': 'Напишите Имя и Фамилию (не длиннее 64 символов)'}, status=400)

    if skill == '' or not valid.validate_comment(skill) or not valid.validate_start(skill):
        return web.json_response({'error': 'Ответьте на вопросы об уровне игры (не длиннее 300 символов)'}, status=400)

    # Ссылка на профиль Telegram — как в боте
    if tg_user.get('username'):
        user_link = f"https://t.me/{tg_user['username']}".lower()
    else:
        user_link = ""

    async with get_db() as session:  # Используем контекстный менеджер

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if user:
            return web.json_response({'error': 'Вы уже зарегистрированы — закройте и откройте приложение ещё раз'}, status=400)

        # Игрок уже играл раньше — возвращаем ему старый дивизион
        old_user = (await session.scalars(select(OldUsers).where(OldUsers.tg_old_users_id == user_id))).first()

        if old_user:
            new_user = User(tg_user_id = user_id, name_user = name, link = user_link, division_level = old_user.division_level, skill = skill)
        else:
            new_user = User(tg_user_id = user_id, name_user = name, link = user_link, skill = skill)

        session.add(new_user)

    print(f"🙋‍♂️ Новый пользователь зарегистрировался в приложении (id {user_id})!")
    return web.json_response({'ok': True})
