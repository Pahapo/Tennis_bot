from sqlalchemy.ext.asyncio import AsyncSession

import handlers.gold as g

from sqlalchemy import select
from models.PlayerSkin import PlayerSkin

# Скины как в Clash Royale: фон (арена) + герой на нём + ракетка на главном экране. Покупаются за монеты 🪙.
# Картинки: /static/img/skins/<id>.svg (у ракеток — картинка для магазина, на главном экране ракетка рисуется в CSS)

DEFAULT_HERO = 'hero_novice'   # Герой по умолчанию — есть у всех бесплатно
DEFAULT_BACKGROUND = None      # Фон по умолчанию — стандартный корт (bg_default.svg), с лигой не связан
DEFAULT_RACKET = 'racket_wood' # Ракетка по умолчанию — деревянная, есть у всех бесплатно

RARITY_NAMES = {
    'common': 'Обычный',
    'rare': 'Редкий',
    'epic': 'Эпический',
    'legendary': 'Легендарный'
}

# min_league — купить можно только с этой лиги (в текущем сезоне)
# months — сезонный скин, продаётся только в эти месяцы (купленный остаётся навсегда)
SKINS = [
    {'id': 'hero_novice', 'type': 'hero', 'name': 'Новичок', 'rarity': 'common', 'price': 0, 'min_league': None, 'months': None},
    {'id': 'hero_pro', 'type': 'hero', 'name': 'Профи в белом', 'rarity': 'common', 'price': 150, 'min_league': None, 'months': None},
    {'id': 'hero_ninja', 'type': 'hero', 'name': 'Ниндзя', 'rarity': 'rare', 'price': 400, 'min_league': None, 'months': None},
    {'id': 'hero_robot', 'type': 'hero', 'name': 'Робот', 'rarity': 'rare', 'price': 400, 'min_league': None, 'months': None},
    {'id': 'hero_knight', 'type': 'hero', 'name': 'Рыцарь', 'rarity': 'epic', 'price': 900, 'min_league': None, 'months': None},
    {'id': 'hero_dragon', 'type': 'hero', 'name': 'Дракон', 'rarity': 'legendary', 'price': 2000, 'min_league': 7, 'months': None},
    {'id': 'hero_santa', 'type': 'hero', 'name': 'Дед Мороз', 'rarity': 'epic', 'price': 900, 'min_league': None, 'months': [12, 1]},

    {'id': 'bg_beach', 'type': 'background', 'name': 'Пляжный корт', 'rarity': 'common', 'price': 150, 'min_league': None, 'months': None},
    {'id': 'bg_garden', 'type': 'background', 'name': 'Японский сад', 'rarity': 'rare', 'price': 400, 'min_league': None, 'months': None},
    {'id': 'bg_snow', 'type': 'background', 'name': 'Снежный корт', 'rarity': 'rare', 'price': 400, 'min_league': None, 'months': None},
    {'id': 'bg_city', 'type': 'background', 'name': 'Ночной город', 'rarity': 'epic', 'price': 900, 'min_league': None, 'months': None},
    {'id': 'bg_space', 'type': 'background', 'name': 'Космос', 'rarity': 'legendary', 'price': 2000, 'min_league': 8, 'months': None},
    {'id': 'bg_newyear', 'type': 'background', 'name': 'Новогодний корт', 'rarity': 'epic', 'price': 900, 'min_league': None, 'months': [12, 1]},

    {'id': 'racket_wood', 'type': 'racket', 'name': 'Деревянная', 'rarity': 'common', 'price': 0, 'min_league': None, 'months': None},
    {'id': 'racket_teal', 'type': 'racket', 'name': 'Бирюза', 'rarity': 'common', 'price': 150, 'min_league': None, 'months': None},
    {'id': 'racket_gold', 'type': 'racket', 'name': 'Про-тур', 'rarity': 'rare', 'price': 400, 'min_league': None, 'months': None},
    {'id': 'racket_crystal', 'type': 'racket', 'name': 'Кристалл', 'rarity': 'epic', 'price': 900, 'min_league': None, 'months': None},
    {'id': 'racket_neon', 'type': 'racket', 'name': 'Карбон и неон', 'rarity': 'epic', 'price': 900, 'min_league': None, 'months': None}
]


def find_skin(skin_id):  # Скин по id (или None)
    for skin in SKINS:
        if skin['id'] == skin_id:
            return skin
    return None


def is_on_sale(skin):  # Сезонный скин продаётся только в свои месяцы
    if skin['months'] == None:
        return True
    return g.now_moscow().month in skin['months']


async def get_owned_skins(user_id, session: AsyncSession):  # id купленных скинов (+ бесплатные герой и ракетка)
    rows = (await session.scalars(select(PlayerSkin).where(PlayerSkin.tg_user_id == user_id))).all()
    owned = [DEFAULT_HERO, DEFAULT_RACKET]
    for row in rows:
        owned.append(row.skin_id)
    return owned


def get_hero(progress):  # Надетый герой
    if progress.skin_hero and find_skin(progress.skin_hero):
        return progress.skin_hero
    return DEFAULT_HERO


def get_background(progress):  # Надетый фон (None — стандартный фон)
    if progress.skin_background and find_skin(progress.skin_background):
        return progress.skin_background
    return DEFAULT_BACKGROUND


def get_racket(progress):  # Надетая ракетка
    if progress.skin_racket and find_skin(progress.skin_racket):
        return progress.skin_racket
    return DEFAULT_RACKET


async def buy_skin(user_id, skin_id, session: AsyncSession):  # Покупка за монеты. Возвращает текст ошибки или None
    # Сначала блокируем строку игрока — два одновременных нажатия не купят скин дважды
    progress = await g.get_progress(user_id, session)

    skin = find_skin(skin_id)

    if skin == None or skin['price'] == 0:
        return 'Такого скина нет в магазине'

    if skin_id in await get_owned_skins(user_id, session):
        return 'Этот скин уже у вас'

    if not is_on_sale(skin):
        return 'Этот сезонный скин сейчас не продаётся'

    if skin['min_league'] != None and g.get_league(progress.season_gold) < skin['min_league']:
        return f"Скин откроется в {skin['min_league']}-й лиге"

    if not await g.spend_gold(user_id, skin['price'], 'skin', session, comment = f"Скин «{skin['name']}»"):
        return 'Не хватает монет 🪙'

    session.add(PlayerSkin(tg_user_id = user_id, skin_id = skin_id, date = g.now_moscow()))
    await session.flush()  # Сразу записываем покупку, чтобы скин можно было тут же надеть (autoflush выключен)
    return None


async def equip_skin(user_id, skin_id, session: AsyncSession):  # Надеть скин. skin_id = 'default' — вернуть стандартный фон
    progress = await g.get_progress(user_id, session)

    if skin_id == 'default':
        progress.skin_background = None
        return None

    skin = find_skin(skin_id)
    if skin == None or skin_id not in await get_owned_skins(user_id, session):
        return 'Сначала купите этот скин'

    if skin['type'] == 'hero':
        progress.skin_hero = skin_id
    elif skin['type'] == 'racket':
        progress.skin_racket = skin_id
    else:
        progress.skin_background = skin_id
    return None
