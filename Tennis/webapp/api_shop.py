import os
import re
from datetime import timedelta
from aiohttp import web

import handlers.gold as g
import handlers.skins as sk
import handlers.market_app as mk
import handlers.tournament_app as ta
from webapp.auth import get_tg_user
from webapp.api_match import read_json

from config.db_utils import get_db, get_db_readonly
from sqlalchemy import select
from models.User import User
from models.Inventory import Inventory
from models.MarketListing import MarketListing

INVENTORY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img', 'inventory')  # Фото товаров клуба
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10 МБ на фото

# Товары клуба: первая цифра в названии фото — категория (как в боте: 1.1, 2.1, 3.2 ...)
CLUB_CATEGORIES = {'1': 'Теннисные мячи 🎾', '2': 'Виброгаситель ⚡️', '3': 'Намотка 💫'}
MANAGER_LINK = 'https://t.me/sup_MM'  # Менеджер клуба: ему пишут, чтобы купить товар клуба


def find_price(text):  # Цена из описания товара: "Банка 3 шт. — 25 руб." -> 25.0 (или None)
    found = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:бел\.?\s*)?руб', text)
    if found == None:
        return None
    return float(found.group(1).replace(',', '.'))


# ---------- Скины ----------

# GET /api/skins — каталог скинов: что куплено, что надето, что можно купить
async def api_skins(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']

    async with get_db() as session:  # get_db: прогресс игрока может создаться при первом заходе

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        progress = await g.get_progress(user_id, session)
        owned = await sk.get_owned_skins(user_id, session)
        league = g.get_league(progress.season_gold)

        skins = []
        for skin in sk.SKINS:
            locked_text = None
            if skin['min_league'] != None and league < skin['min_league']:
                locked_text = f"🔒 С {skin['min_league']}-й лиги"
            elif not sk.is_on_sale(skin):
                locked_text = '❄️ Сезонный — сейчас не продаётся'

            skins.append({
                'id': skin['id'],
                'type': skin['type'],
                'name': skin['name'],
                'rarity': skin['rarity'],
                'rarity_name': sk.RARITY_NAMES[skin['rarity']],
                'price': skin['price'],
                'seasonal': skin['months'] != None,
                'owned': skin['id'] in owned,
                'locked_text': locked_text
            })

        result = {
            'skins': skins,
            'hero': sk.get_hero(progress),
            'background': sk.get_background(progress),
            'racket': sk.get_racket(progress),
            'gold': progress.gold
        }

    return web.json_response(result)


# POST /api/skins/buy — купить скин за монеты: {skin_id}
async def api_skins_buy(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    data = await read_json(request)

    async with get_db() as session:  # Используем контекстный менеджер
        error = await sk.buy_skin(tg_user['id'], data.get('skin_id'), session)
        if error:
            return web.json_response({'error': error}, status=400)

        # Купленный скин сразу надеваем
        await sk.equip_skin(tg_user['id'], data.get('skin_id'), session)

    return web.json_response({'ok': True})


# POST /api/skins/equip — надеть купленный скин: {skin_id} ('default' — вернуть стандартный фон)
async def api_skins_equip(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    data = await read_json(request)

    async with get_db() as session:  # Используем контекстный менеджер
        error = await sk.equip_skin(tg_user['id'], data.get('skin_id'), session)
        if error:
            return web.json_response({'error': error}, status=400)

    return web.json_response({'ok': True})


# ---------- Барахолка ----------

def listing_card(listing, seller):  # Данные объявления для фронта
    photos = []
    for name in mk.get_photos(listing):
        photos.append('/market_img/' + name)

    expired = listing.status == 'active' and listing.expires != None and listing.expires < g.now_moscow()

    return {
        'id': listing.id_listing,
        'title': listing.title,
        'description': listing.description,
        'price': listing.price,
        'category': listing.category,
        'condition': listing.item_condition,
        'photos': photos,
        'status': listing.status,
        'expired': expired,
        'expires': listing.expires.strftime("%d.%m.%Y") if listing.expires else None,
        'seller_name': seller.name_user if seller else '',
        'seller_link': seller.link if seller else ''
    }


async def count_active_listings(user_id, session):  # Объявления на проверке и в продаже (не истёкшие)
    listings = (await session.scalars(select(MarketListing).where(
        (MarketListing.tg_user_id == user_id) & ((MarketListing.status == 'moderation') | (MarketListing.status == 'active'))
    ))).all()

    count = 0
    for listing in listings:
        if listing.status == 'moderation' or listing.expires == None or listing.expires >= g.now_moscow():
            count += 1
    return count


# GET /api/market — товары клуба, объявления игроков и мои объявления
async def api_market(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']
    now = g.now_moscow()

    async with get_db_readonly() as session:  # Используем контекстный менеджер

        # Товары клуба по категориям (таблица inventory, как в боте)
        club = []
        for key in CLUB_CATEGORIES:
            # Картинка категории: N.jpg (как в шапке категории в боте)
            category_photo = None
            if os.path.exists(os.path.join(INVENTORY_DIR, key + '.jpg')):
                category_photo = '/inventory_img/' + key + '.jpg'

            club.append({'key': key, 'name': CLUB_CATEGORIES[key], 'photo': category_photo, 'items': []})

        for item in (await session.scalars(select(Inventory).order_by(Inventory.photo))).all():
            key = (item.photo or '')[:1]
            if key not in CLUB_CATEGORIES:
                continue

            photo = None
            if item.photo and os.path.exists(os.path.join(INVENTORY_DIR, item.photo + '.jpg')):
                photo = '/inventory_img/' + item.photo + '.jpg'

            description = ta.clean_html(item.description)

            price = item.price
            if price == None:
                price = find_price(description)

            for category in club:
                if category['key'] == key:
                    category['items'].append({'id': item.inventory_id, 'photo': photo, 'description': description, 'price': price})

        # Объявления игроков в продаже (сначала новые)
        listings = []
        active = (await session.scalars(select(MarketListing).where((MarketListing.status == 'active') & (MarketListing.expires >= now)).order_by(MarketListing.id_listing.desc()))).all()
        for listing in active:
            seller = (await session.scalars(select(User).where(User.tg_user_id == listing.tg_user_id))).first()
            card = listing_card(listing, seller)
            card['mine'] = listing.tg_user_id == user_id
            listings.append(card)

        # Мои объявления (кроме удалённых)
        mine = []
        my_listings = (await session.scalars(select(MarketListing).where((MarketListing.tg_user_id == user_id) & (MarketListing.status != 'deleted')).order_by(MarketListing.id_listing.desc()))).all()
        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()
        for listing in my_listings:
            mine.append(listing_card(listing, user))

    return web.json_response({
        'club': club,
        'manager_link': MANAGER_LINK,
        'listings': listings,
        'mine': mine,
        'categories': mk.CATEGORIES,
        'conditions': mk.CONDITIONS,
        'max_photos': mk.MAX_PHOTOS
    })


# POST /api/market/create — новое объявление (форма multipart: title, description, price, category, condition, photos)
async def api_market_create(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    user_id = tg_user['id']
    bot = request.app['bot']

    try:
        form = await request.post()
    except Exception:
        return web.json_response({'error': 'Не удалось прочитать данные, попробуйте ещё раз'}, status=400)

    title = str(form.get('title') or '').strip()
    description = str(form.get('description') or '').strip()
    category = form.get('category')
    condition = form.get('condition')

    if title == '' or len(title) > 60:
        return web.json_response({'error': 'Название — от 1 до 60 символов'}, status=400)
    if len(description) > 500:
        return web.json_response({'error': 'Описание — не больше 500 символов'}, status=400)
    if category not in mk.CATEGORIES:
        return web.json_response({'error': 'Выберите категорию'}, status=400)
    if condition not in mk.CONDITIONS:
        return web.json_response({'error': 'Выберите состояние'}, status=400)

    try:
        price = round(float(str(form.get('price')).replace(',', '.')), 2)
    except ValueError:
        return web.json_response({'error': 'Укажите цену числом'}, status=400)
    if price < 0 or price > 100000:
        return web.json_response({'error': 'Укажите цену числом'}, status=400)

    # Фото: от 1 до 3 картинок
    photo_fields = form.getall('photos', [])
    if len(photo_fields) == 0:
        return web.json_response({'error': 'Добавьте хотя бы одно фото'}, status=400)
    if len(photo_fields) > mk.MAX_PHOTOS:
        return web.json_response({'error': f'Не больше {mk.MAX_PHOTOS} фото'}, status=400)

    photos_bytes = []
    for field in photo_fields:
        if not hasattr(field, 'file') or not (field.content_type or '').startswith('image/'):
            return web.json_response({'error': 'Можно прикрепить только картинки'}, status=400)
        photo_bytes = field.file.read()
        if len(photo_bytes) == 0 or len(photo_bytes) > MAX_PHOTO_SIZE:
            return web.json_response({'error': 'Каждое фото — не больше 10 МБ'}, status=400)
        photos_bytes.append(photo_bytes)

    async with get_db() as session:  # Используем контекстный менеджер

        user = (await session.scalars(select(User).where(User.tg_user_id == user_id))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        # Покупатели пишут продавцу в Telegram — без username это невозможно
        if not user.link:
            return web.json_response({'error': 'Чтобы продавать, укажите username в настройках Telegram — по нему покупатели напишут вам'}, status=400)

        if await count_active_listings(user_id, session) >= mk.MAX_ACTIVE:
            return web.json_response({'error': f'У вас уже {mk.MAX_ACTIVE} объявлений. Отметьте проданное или удалите старое'}, status=400)

        listing = MarketListing(tg_user_id = user_id, title = title, description = description or None, price = price, category = category, item_condition = condition, photos = '', created = g.now_moscow())
        session.add(listing)
        await session.flush()  # Чтобы получить id_listing

        # Сохраняем фото: Tennis/img/market/<id объявления>_<номер>.jpg
        os.makedirs(mk.MARKET_DIR, exist_ok=True)
        names = []
        for i in range(len(photos_bytes)):
            name = f"{listing.id_listing}_{i + 1}.jpg"
            with open(os.path.join(mk.MARKET_DIR, name), "wb") as photo_file:
                photo_file.write(photos_bytes[i])
            names.append(name)
        listing.photos = ','.join(names)

        await mk.send_to_moderation(listing, user, bot)

    print(f"✅ Игрок с id {user_id} создал объявление на барахолке (на модерации)")
    return web.json_response({'ok': True})


# POST /api/market/action — моё объявление: {listing_id, action: sold / delete / prolong}
async def api_market_action(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    data = await read_json(request)
    action = data.get('action')

    async with get_db() as session:  # Используем контекстный менеджер

        listing = (await session.scalars(select(MarketListing).where(MarketListing.id_listing == data.get('listing_id')).with_for_update())).first()

        if listing == None or listing.tg_user_id != tg_user['id'] or listing.status == 'deleted':
            return web.json_response({'error': 'Объявление не найдено'}, status=404)

        if action == 'sold':
            listing.status = 'sold'
        elif action == 'delete':
            listing.status = 'deleted'
        elif action == 'prolong':
            if listing.status != 'active':
                return web.json_response({'error': 'Продлить можно только опубликованное объявление'}, status=400)
            listing.expires = g.now_moscow() + timedelta(days=mk.LIFETIME_DAYS)
        else:
            return web.json_response({'error': 'Неизвестное действие'}, status=400)

    return web.json_response({'ok': True})
