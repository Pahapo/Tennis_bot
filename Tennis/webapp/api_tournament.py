import os
from aiohttp import web
from config.config import CHANNEL

import handlers.gold as g
import handlers.functions as f
import handlers.match_app as ma
import handlers.btn_tournaments as bt
import handlers.tournament_app as ta
from webapp.auth import get_tg_user
from webapp.api_match import read_json

from config.db_utils import get_db, get_db_readonly
from sqlalchemy import select
from models.User import User
from models.Tournament import Tournament
from models.TournamentPlayers import TournamentPlayers
from models.PaymentMethod import PaymentMethod
from models.PaymentRequest import PaymentRequest

# Папка, куда бот сохраняет чеки (та же, что в handlers/payment.py)
PAYMENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img', 'payment')
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10 МБ


# GET /api/tournaments — турниры для записи, таблицы и мои идущие турниры
async def api_tournaments(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']

    async with get_db() as session:  # get_db: check_ban_user снимает закончившийся бан

        await f.check_ban_user(user_id, session)

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        division_names = await ta.get_division_names(session)

        # Турниры, на которые идёт запись
        tournaments = []
        for tournament in await ta.get_open_tournaments(session):
            status, division_level = await ta.tournament_status(tournament, user, session)

            names = []
            for division_id in map(int, tournament.division.split(",")):
                if division_id in division_names:
                    names.append(division_names[division_id])

            tournaments.append({
                'id': tournament.tournament_id,
                'name': tournament.name_tournament,
                'divisions': ', '.join(names),
                'type': tournament.type,
                'quantity': tournament.quantity_person,
                'start': tournament.start_tournament,
                'end': tournament.end_tournament,
                'price': tournament.price,
                'regulations': ta.clean_html(tournament.regulations),
                'status': status,
                'division_name': division_names.get(division_level)
            })

        # Ссылки на таблицы (как в разделе "Турнирные таблицы" бота)
        active_tables = []
        for name, link in (await bt.get_links_tournaments(session)).items():
            if link:
                active_tables.append({'name': name, 'link': link})

        history_tables = []
        for name, link in (await bt.get_history_links_tournaments(session)).items():
            if link:
                history_tables.append({'name': name, 'link': link})

        # Мои идущие турниры и их участники — для записи счёта
        running = []
        for tournament in await ta.get_running_tournaments(user_id, session):
            rows = (await session.scalars(select(TournamentPlayers).where(TournamentPlayers.id_tournament == tournament.tournament_id))).all()

            players = []
            added = []
            for row in rows:
                if row.id_tg_user == user_id or row.id_tg_user in added:
                    continue
                added.append(row.id_tg_user)
                player = (await session.scalars(select(User).where(User.tg_user_id == row.id_tg_user))).first()
                if player:
                    players.append({'id': player.tg_user_id, 'name': player.name_user, 'division': division_names.get(player.division_level, 'Не определён')})

            players.sort(key=lambda player: player['name'] or '')
            running.append({'id': tournament.tournament_id, 'name': tournament.name_tournament, 'players': players})

        payment_method = (await session.scalars(select(PaymentMethod).where(PaymentMethod.payment_method_id == 1))).first()
        payment = None
        if payment_method:
            payment = {'account': payment_method.payment_method, 'bank': payment_method.bank_name}

        crystals = ta.get_crystals(user)

    return web.json_response({
        'tournaments': tournaments,
        'active_tables': active_tables,
        'history_tables': history_tables,
        'running': running,
        'payment': payment,
        'crystals': crystals,
        'can_use_crystals': not ta.is_staff(user_id),
        'min_crystals': ta.MIN_CRYSTALS,
        'crystals_per_ruble': ta.CRYSTALS_PER_RUBLE
    })


# POST /api/tournaments/pay — запись на турнир: чек об оплате (фото) + кристаллы. Форма multipart: tournament_id, crystals, photo
async def api_tournaments_pay(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']
    bot = request.app['bot']

    if not await f.check_subscription(user_id, bot):
        return web.json_response({'error': 'not_subscribed', 'channel': CHANNEL}, status=403)

    try:
        form = await request.post()
        tournament_id = int(form.get('tournament_id'))
        crystals = int(form.get('crystals') or 0)
    except (ValueError, TypeError):
        return web.json_response({'error': 'Не удалось прочитать данные, попробуйте ещё раз'}, status=400)

    photo = form.get('photo')
    if photo == None or not hasattr(photo, 'file'):
        return web.json_response({'error': 'Прикрепите скриншот чека об оплате'}, status=400)

    if not (photo.content_type or '').startswith('image/'):
        return web.json_response({'error': 'Чек должен быть картинкой (скриншот или фото)'}, status=400)

    photo_bytes = photo.file.read()
    if len(photo_bytes) == 0 or len(photo_bytes) > MAX_PHOTO_SIZE:
        return web.json_response({'error': 'Фото чека должно быть не больше 10 МБ'}, status=400)

    async with get_db() as session:  # Используем контекстный менеджер

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
        tournament = (await session.scalars(select(Tournament).where(Tournament.tournament_id == tournament_id))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        if tournament == None or not ta.is_open(tournament):
            return web.json_response({'error': 'Запись на этот турнир уже закрыта'}, status=400)

        status, division_level = await ta.tournament_status(tournament, user, session)

        if status not in ['can_register', 'can_register_second']:
            return web.json_response({'error': 'Записаться на этот турнир сейчас нельзя — обновите страницу'}, status=400)

        # Кристаллы
        if crystals != 0 and ta.is_staff(user_id):
            return web.json_response({'error': 'Редакторы не могут применять кристаллы'}, status=400)

        error = ta.check_crystals(crystals, ta.get_crystals(user), tournament.price or 0)
        if error:
            return web.json_response({'error': error}, status=400)

        price = ta.price_with_crystals(tournament.price or 0, crystals)

        # Сохраняем чек так же, как бот: Tennis/img/payment/<id игрока>_<id турнира>.jpg
        os.makedirs(PAYMENT_DIR, exist_ok=True)
        file_name = f"{user_id}_{tournament_id}"
        copy_number = 1
        while os.path.exists(os.path.join(PAYMENT_DIR, file_name + ".jpg")):
            file_name = f"{user_id}_{tournament_id}_{copy_number}"
            copy_number += 1

        photo_path = os.path.join(PAYMENT_DIR, file_name + ".jpg")
        with open(photo_path, "wb") as photo_file:
            photo_file.write(photo_bytes)

        payment_request = PaymentRequest(tg_user_id = user_id, tournament_id = tournament_id, division_level = division_level, price = price, crystals = crystals, photo = file_name, date = g.now_moscow())
        session.add(payment_request)
        await session.flush()  # Чтобы получить id_request

        division_names = await ta.get_division_names(session)
        await ta.send_payment_to_editors(payment_request, user, tournament, division_names.get(division_level, 'Не определён'), photo_path, bot)

    print(f"✅ Игроком с id {user_id} отправлен чек об оплате для участия в турнире {tournament.name_tournament} (Mini App). Чек: '{photo_path}'")
    return web.json_response({'ok': True})


# POST /api/tournaments/score — счёт турнирной игры: {tournament_id, opponent_id, sets}
async def api_tournaments_score(request):
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

    score = checked[0]  # Счёт с моей стороны: "6:4 6:3"

    async with get_db_readonly() as session:  # Используем контекстный менеджер

        running = await ta.get_running_tournaments(user_id, session)
        tournament_ids = []
        for tournament in running:
            tournament_ids.append(tournament.tournament_id)

        if data.get('tournament_id') not in tournament_ids:
            return web.json_response({'error': 'Выберите турнир, в котором вы играете'}, status=400)

        opponent_row = (await session.scalars(select(TournamentPlayers).where((TournamentPlayers.id_tournament == data.get('tournament_id')) & (TournamentPlayers.id_tg_user == data.get('opponent_id'))))).first()

        if opponent_row == None or data.get('opponent_id') == user_id:
            return web.json_response({'error': 'Выберите соперника из участников турнира'}, status=400)

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
        contestant = (await session.scalars(select(User).where(User.tg_user_id == data.get('opponent_id')))).first()

    # Подтверждение турнирного счёта ищет игроков по username — без него не сработает
    if not user.link:
        return web.json_response({'error': 'У вас в Telegram не указан username — без него счёт турнира не записать'}, status=400)
    if not contestant.link:
        return web.json_response({'error': 'У соперника в Telegram не указан username — счёт турнира запишет только он сам'}, status=400)

    await ta.send_tournament_score(user, contestant, score, bot)

    return web.json_response({'ok': True})
