from html import escape
from datetime import datetime, timedelta
from aiohttp import web
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.config import CHANNEL

import handlers.gold as g
import handlers.functions as f
import handlers.match_app as ma
import handlers.validation as valid
from webapp.auth import get_tg_user

from config.db_utils import get_db, get_db_readonly
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.User import User
from models.Division import Division
from models.Match import Match
from models.MatchReward import MatchReward


# ---------- Вспомогательные функции ----------

async def read_json(request):  # Тело запроса (пустой словарь, если прислали что-то не то)
    try:
        data = await request.json()
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


async def player_card(user_id, session: AsyncSession):  # Короткие данные игрока для карточек игр
    user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

    if user == None:
        return {'id': user_id, 'name': 'Игрок', 'link': '', 'division': 'Не определён', 'rating': None}

    division_name = 'Не определён'
    if user.division_level != None:
        division = (await session.scalars(select(Division).where(Division.division_id == user.division_level))).first()
        if division:
            division_name = division.name_division

    return {
        'id': user.tg_user_id,
        'name': user.name_user,
        'link': user.link,
        'division': division_name,
        'rating': user.rating
    }


async def match_card(match, session: AsyncSession):  # Данные игры для фронта
    players = []
    for player in ma.get_players(match):
        players.append(await player_card(player, session))

    if match.type == 'Парный':
        places = 4
    else:
        places = 2

    return {
        'id': match.match_id,
        'date': match.date_booking or match.date_without_booking,
        'booked': match.date_booking != None,
        'court': match.name_court,
        'type': match.type,
        'comment': match.comment,
        'creator_id': match.id_tg_user,
        'players': players,
        'places': places,
        'status': match.status,
        'score': match.score,
        'team_1': ma.ids_from_text(match.team_1),
        'team_2': ma.ids_from_text(match.team_2)
    }


def is_my_match(match, user_id):  # Игрок участвует в игре
    return user_id in ma.get_players(match)


# ---------- Поиск соперника ----------

# GET /api/matches/search — открытые игры других игроков
async def api_matches_search(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']
    now = g.now_moscow()

    async with get_db_readonly() as session:  # Используем контекстный менеджер

        matches = (await session.scalars(select(Match).where(Match.status == None))).all()

        result = []
        for match in matches:
            if ma.is_match_full(match) or is_my_match(match, user_id):
                continue
            if ma.get_match_date(match) < now:
                continue
            result.append(await match_card(match, session))

    result.sort(key=lambda card: datetime.strptime(card['date'], "%H:%M %d.%m.%Y"))
    return web.json_response(result)


# GET /api/matches/mine — мои заявки и мои игры
async def api_matches_mine(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']
    month_ago = g.now_moscow() - timedelta(days=30)

    async with get_db_readonly() as session:  # Используем контекстный менеджер

        matches = (await session.scalars(select(Match).where(
            (Match.player_1 == user_id) | (Match.player_2 == user_id) | (Match.player_3 == user_id) | (Match.player_4 == user_id)
        ))).all()

        requests = []
        games = []

        for match in matches:
            card = await match_card(match, session)

            # Свои игры, где ещё не набран состав — это "Мои заявки"
            if match.id_tg_user == user_id and not ma.is_match_full(match):
                requests.append(card)
                continue

            # Завершённые игры показываем за последний месяц
            if match.status == 'done' and ma.get_match_date(match) < month_ago:
                continue

            # Сколько монет я получил за эту игру
            card['my_reward'] = None
            if match.status == 'done':
                reward = (await session.scalars(select(MatchReward).where((MatchReward.match_id == match.match_id) & (MatchReward.tg_user_id == user_id)))).first()
                if reward:
                    card['my_reward'] = reward.amount

            games.append(card)

    requests.sort(key=lambda card: datetime.strptime(card['date'], "%H:%M %d.%m.%Y"))
    games.sort(key=lambda card: datetime.strptime(card['date'], "%H:%M %d.%m.%Y"), reverse=True)

    return web.json_response({'requests': requests, 'games': games, 'courts': ma.COURTS})


# POST /api/matches/create — новая заявка на игру
async def api_matches_create(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']
    bot = request.app['bot']
    data = await read_json(request)

    if not await f.check_subscription(user_id, bot):
        return web.json_response({'error': 'not_subscribed', 'channel': CHANNEL}, status=403)

    # Дата из поля "datetime-local": "2026-05-20T18:30"
    try:
        match_date = datetime.strptime(str(data.get('date')), "%Y-%m-%dT%H:%M")
    except ValueError:
        return web.json_response({'error': 'Укажите дату и время игры'}, status=400)

    if match_date < g.now_moscow():
        return web.json_response({'error': 'Дата игры уже прошла'}, status=400)

    match_type = data.get('type')
    if match_type not in ['Одиночный', 'Парный']:
        return web.json_response({'error': 'Выберите тип игры'}, status=400)

    court = None
    if data.get('booked') == True:
        court = data.get('court')
        if court not in ma.COURTS:
            return web.json_response({'error': 'Выберите забронированный корт'}, status=400)

    comment = str(data.get('comment') or '').strip()
    if not valid.validate_comment(comment):
        return web.json_response({'error': 'Комментарий длиннее 300 символов'}, status=400)
    if comment == '':
        comment = None

    date_text = match_date.strftime("%H:%M %d.%m.%Y")

    async with get_db() as session:  # Используем контекстный менеджер

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        # Возраст и пол спрашиваем один раз, как в боте
        if not user.age:
            age = str(data.get('age') or '').strip()
            if not valid.validate_age(age):
                return web.json_response({'error': 'Укажите возраст целым числом'}, status=400)
            user.age = int(age)

        if not user.sex:
            if data.get('sex') not in ['Мужчина', 'Женщина']:
                return web.json_response({'error': 'Укажите пол'}, status=400)
            user.sex = data.get('sex')

        # Не больше 3 открытых заявок
        my_matches = (await session.scalars(select(Match).where((Match.id_tg_user == user_id) & (Match.status == None)))).all()
        open_requests = 0
        for match in my_matches:
            if not ma.is_match_full(match):
                open_requests += 1

        if open_requests >= ma.MAX_OPEN_REQUESTS:
            return web.json_response({'error': f'У вас уже {ma.MAX_OPEN_REQUESTS} открытые заявки. Удалите одну, чтобы создать новую'}, status=400)

        if court:
            new_match = Match(id_tg_user = user_id, date_booking = date_text, name_court = court, type = match_type, comment = comment, player_1 = user_id)
        else:
            new_match = Match(id_tg_user = user_id, date_without_booking = date_text, type = match_type, comment = comment, player_1 = user_id)
        session.add(new_match)

        await f.check_ban_user(user_id, session)

    print(f'✅ Карточка игры создана пользователем с ID {user_id} (Mini App)!')
    return web.json_response({'ok': True})


# POST /api/matches/delete — удалить свою заявку (пока состав не набран)
async def api_matches_delete(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']
    bot = request.app['bot']
    data = await read_json(request)

    async with get_db() as session:  # Используем контекстный менеджер

        match = (await session.scalars(select(Match).where(Match.match_id == data.get('match_id')).with_for_update())).first()

        if match == None or match.id_tg_user != user_id:
            return web.json_response({'error': 'Заявка не найдена'}, status=404)

        if ma.is_match_full(match) or match.status != None:
            return web.json_response({'error': 'Состав уже собран — эту игру удалить нельзя'}, status=400)

        date = match.date_booking or match.date_without_booking
        others = []
        for player in ma.get_players(match):
            if player != user_id:
                others.append(player)

        await session.delete(match)

    # Тем, кто уже записался (в парной игре), сообщаем об отмене
    for player in others:
        await ma.notify(bot, player, f"😥 <b>Игра {date} отменена</b> создателем")

    return web.json_response({'ok': True})


# POST /api/matches/apply — откликнуться на игру. Создателю придёт сообщение с кнопками "Принять / Отклонить"
async def api_matches_apply(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']
    bot = request.app['bot']
    data = await read_json(request)

    if not await f.check_subscription(user_id, bot):
        return web.json_response({'error': 'not_subscribed', 'channel': CHANNEL}, status=403)

    async with get_db_readonly() as session:  # Используем контекстный менеджер

        match = (await session.scalars(select(Match).where(Match.match_id == data.get('match_id')))).first()

        if match == None or match.status != None or ma.is_match_full(match):
            return web.json_response({'error': 'Эта игра уже недоступна'}, status=400)

        if is_my_match(match, user_id):
            return web.json_response({'error': 'Вы уже в этой игре'}, status=400)

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        date = match.date_booking or match.date_without_booking
        text = f"<b>Пользователь 🙋‍♂️ <a href='{escape(user.link or '')}'>{escape(user.name_user or '')}</a> откликнулся(-ась) на вашу заявку!</b>\n\n⏰ <b>Дата игры:</b> {date}\n🎾 <b>Тип игры:</b> {match.type}\n\n<b>СОПЕРНИК:</b>\n{(await user.build_repr_data())}"
        creator_id = match.id_tg_user
        match_id = match.match_id

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='❌ Отклонить', callback_data=f'ma_no:{match_id}:{user_id}'),
                                                      InlineKeyboardButton(text='✅ Принять', callback_data=f'ma_yes:{match_id}:{user_id}')]])
    await ma.notify(bot, creator_id, text, keyboard)

    return web.json_response({'ok': True})


# ---------- Счёт ----------

# GET /api/score/pending — игры, где я могу записать счёт
async def api_score_pending(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']

    async with get_db_readonly() as session:  # Используем контекстный менеджер

        matches = (await session.scalars(select(Match).where(Match.status == 'wait_score'))).all()

        result = []
        for match in matches:
            if not is_my_match(match, user_id):
                continue
            # После "Не согласен" счёт вводит только тот, кто не согласился
            if match.score_turn != None and match.score_turn != user_id:
                continue
            result.append(await match_card(match, session))

    return web.json_response(result)


# POST /api/score/submit — записать счёт: {match_id, partner_id (для парной), sets: [[6, 4], [3, 6], [7, 5]]}
async def api_score_submit(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']
    bot = request.app['bot']
    data = await read_json(request)

    try:
        checked = ma.check_sets(data.get('sets') or [])
    except (ValueError, TypeError):
        checked = None

    if checked == None:
        return web.json_response({'error': 'Проверьте счёт: в каждом сете должен быть победитель, и ничьей быть не может'}, status=400)

    score = checked[0]  # Счёт со стороны моей команды

    async with get_db() as session:  # Используем контекстный менеджер

        match = (await session.scalars(select(Match).where(Match.match_id == data.get('match_id')).with_for_update())).first()

        if match == None or match.status != 'wait_score' or not is_my_match(match, user_id):
            return web.json_response({'error': 'Счёт по этой игре уже записан'}, status=400)

        if match.score_turn != None and match.score_turn != user_id:
            return web.json_response({'error': 'Сейчас счёт вводит соперник'}, status=400)

        # Команды: моя (я и партнёр) — команда 1, остальные — команда 2
        team_1 = [user_id]
        if match.type == 'Парный':
            partner_id = data.get('partner_id')
            if partner_id == user_id or partner_id not in ma.get_players(match):
                return web.json_response({'error': 'Выберите партнёра по команде'}, status=400)
            team_1.append(partner_id)

        team_2 = []
        for player in ma.get_players(match):
            if player not in team_1:
                team_2.append(player)

        await ma.submit_score(match, user_id, team_1, team_2, score, session, bot)

    return web.json_response({'ok': True})
