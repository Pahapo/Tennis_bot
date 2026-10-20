import os
from aiohttp import web
from config.config import WEBAPP_PORT

from webapp.api_profile import api_me

# Папка с файлами Mini App (html, css, js, картинки)
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'webapp_static')


# Главная страница Mini App
async def index(request):
    return web.FileResponse(os.path.join(STATIC_DIR, 'index.html'))


# Запуск веб-сервера рядом с ботом (в том же процессе)
async def start_webapp():
    app = web.Application()

    app.router.add_get('/', index)
    app.router.add_get('/api/me', api_me)
    app.router.add_static('/static/', STATIC_DIR)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, '0.0.0.0', WEBAPP_PORT)
    await site.start()

    print(f"Mini App запущен на порту {WEBAPP_PORT}")
