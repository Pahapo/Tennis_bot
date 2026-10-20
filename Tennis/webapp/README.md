# Mini App

Веб-сервер Mini App запускается вместе с ботом (`Tennis/main.py`) в том же процессе.

- `webapp/server.py` — сервер aiohttp: страница, API и статика
- `webapp/auth.py` — проверка подписи `initData` от Telegram
- `webapp/api_profile.py` — `GET /api/me`, данные профиля
- `webapp_static/` — HTML, CSS, JS и картинки

## Переменные в `.env`

```
WEBAPP_URL=https://адрес-mini-app   # только HTTPS, иначе Telegram не откроет
WEBAPP_PORT=8080                    # порт веб-сервера (по умолчанию 8080)
```

Если `WEBAPP_URL` задан, при запуске бот ставит кнопку «Приложение» слева от поля ввода.

## Локальная разработка

1. Создать тестового бота в @BotFather (`/newbot`), его токен — в `TOKEN`.
2. Поднять MySQL, создать базу в `utf8mb4` и выполнить `tennisDB_script.sql`. Указать её в `DATABASE_URL`.
3. Запустить HTTPS-туннель на порт 8080, например:
   `cloudflared tunnel --url http://localhost:8080`
   Полученный адрес `https://....trycloudflare.com` — в `WEBAPP_URL`.
4. Запустить бота как обычно и открыть «Приложение» в чате с тестовым ботом.

Без Telegram (просто в браузере) страница покажет «Откройте приложение в Telegram» — так и должно быть.
