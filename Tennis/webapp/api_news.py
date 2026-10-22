import os
from aiohttp import web

import handlers.gold as g
import handlers.tournament_app as ta
from webapp.auth import get_tg_user

from config.db_utils import get_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.User import User
from models.News import News

# Папка с фото новостей (раньше туда сохранялись рассылки)
NEWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img', 'news')
NEWS_LIMIT = 30  # Сколько последних новостей показываем


async def get_visible_news(user, session: AsyncSession):  # Новости игрока: только личные (о его достижениях)
    # Рассылки админа в приложение больше не попадают — они приходят только в бота
    news_list = (await session.scalars(select(News).where(News.tg_user_id == user.tg_user_id).order_by(News.id_news.desc()).limit(NEWS_LIMIT))).all()
    return news_list


async def count_unread_news(user, last_seen, session: AsyncSession):  # Сколько новостей игрок ещё не видел
    count = 0
    for news in await get_visible_news(user, session):
        if news.id_news > last_seen:
            count += 1
    return count


# GET /api/news — лента новостей
async def api_news(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    async with get_db() as session:  # Используем контекстный менеджер

        user = (await session.scalars(select(User).where(User.tg_user_id == tg_user['id']))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        progress = await g.get_progress(user.tg_user_id, session)

        items = []
        for news in await get_visible_news(user, session):
            photo = None
            if news.photo:
                photo = '/news_img/' + news.photo

            items.append({
                'id': news.id_news,
                'text': ta.clean_html(news.text),
                'photo': photo,
                'link_text': news.link_text,
                'link_url': news.link_url,
                'date': news.date.strftime("%d.%m.%Y"),
                'is_new': news.id_news > progress.last_news_seen
            })

    return web.json_response(items)


# POST /api/news_seen — игрок открыл новости, красный кружок пропадает
async def api_news_seen(request):
    tg_user = get_tg_user(request)

    if tg_user == None:
        return web.json_response({'error': 'unauthorized'}, status=401)

    async with get_db() as session:  # Используем контекстный менеджер

        user = (await session.scalars(select(User).where(User.tg_user_id == tg_user['id']))).first()

        if user == None:
            return web.json_response({'error': 'not_registered'}, status=404)

        progress = await g.get_progress(user.tg_user_id, session)
        news_list = await get_visible_news(user, session)

        if news_list:
            progress.last_news_seen = news_list[0].id_news  # Самая свежая новость

    return web.json_response({'ok': True})
