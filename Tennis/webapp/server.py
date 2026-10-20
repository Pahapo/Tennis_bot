import os
from aiohttp import web
from config.config import WEBAPP_PORT

from webapp.api_profile import api_me
from webapp.api_gold import api_visit, api_gold_history, api_season_seen
from webapp.api_news import api_news, api_news_seen, NEWS_DIR
from webapp.api_tournament import api_tournaments, api_tournaments_pay, api_tournaments_score
from webapp.api_match import api_matches_search, api_matches_mine, api_matches_create, api_matches_delete, api_matches_apply, api_score_pending, api_score_submit

# Папка с файлами Mini App (html, css, js, картинки)
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'webapp_static')


# Главная страница Mini App
async def index(request):
    return web.FileResponse(os.path.join(STATIC_DIR, 'index.html'))


# Запуск веб-сервера рядом с ботом (в том же процессе)
async def start_webapp(bot):
    app = web.Application(client_max_size=11 * 1024 * 1024)  # Чек об оплате — до 10 МБ
    app['bot'] = bot  # Бот нужен API, чтобы отправлять уведомления игрокам

    app.router.add_get('/', index)
    app.router.add_get('/api/me', api_me)
    app.router.add_post('/api/visit', api_visit)
    app.router.add_get('/api/gold_history', api_gold_history)
    app.router.add_post('/api/season_seen', api_season_seen)

    app.router.add_get('/api/matches/search', api_matches_search)
    app.router.add_get('/api/matches/mine', api_matches_mine)
    app.router.add_post('/api/matches/create', api_matches_create)
    app.router.add_post('/api/matches/delete', api_matches_delete)
    app.router.add_post('/api/matches/apply', api_matches_apply)
    app.router.add_get('/api/score/pending', api_score_pending)
    app.router.add_post('/api/score/submit', api_score_submit)

    app.router.add_get('/api/tournaments', api_tournaments)
    app.router.add_post('/api/tournaments/pay', api_tournaments_pay)
    app.router.add_post('/api/tournaments/score', api_tournaments_score)

    app.router.add_get('/api/news', api_news)
    app.router.add_post('/api/news_seen', api_news_seen)

    app.router.add_static('/static/', STATIC_DIR)

    os.makedirs(NEWS_DIR, exist_ok=True)
    app.router.add_static('/news_img/', NEWS_DIR)  # Фото из рассылок

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, '0.0.0.0', WEBAPP_PORT)
    await site.start()

    print(f"Mini App запущен на порту {WEBAPP_PORT}")
