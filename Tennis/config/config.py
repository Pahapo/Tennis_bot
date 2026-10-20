import os
from dotenv import load_dotenv, find_dotenv

# Ищем .env: от папки этого файла вверх (Tennis/config -> Tennis -> Tennis_bot)
dotenv_path = find_dotenv()
if not dotenv_path:
    raise SystemExit("❌ Файл .env не найден. Он должен лежать в папке Tennis_bot (рядом с requirements.txt) и называться ровно .env (не .env.txt)")

load_dotenv(dotenv_path)  # Загружает переменные из .env

# Без этих переменных бот не запустится — проверяем все сразу, чтобы показать понятную ошибку
REQUIRED_VARIABLES = ['TOKEN', 'DATABASE_URL', 'CHANNELS_SUB', 'ADMINS', 'MAIN_EDITOR', 'EDITOR', 'EMAILS']
missing_variables = []
for name in REQUIRED_VARIABLES:
    if not os.getenv(name):
        missing_variables.append(name)

if missing_variables:
    raise SystemExit(f"❌ В файле {dotenv_path} не хватает переменных: {', '.join(missing_variables)}")

# Бот асинхронный — к MySQL он подключается только через драйвер aiomysql
if not os.getenv('DATABASE_URL').startswith('mysql+aiomysql://'):
    raise SystemExit("❌ DATABASE_URL в .env должен начинаться с mysql+aiomysql://\nПример: DATABASE_URL=mysql+aiomysql://root:ПАРОЛЬ@localhost:3306/tennis?charset=utf8mb4")

TOKEN = os.getenv('TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')
CHANNEL = os.getenv('CHANNEL')
CHANNEL_CHAT = os.getenv('CHANNEL_CHAT')
CHANNELS_SUB = list(map(str, os.getenv('CHANNELS_SUB').split(',')))
CHANNEL_SCORES = os.getenv('CHANNEL_SCORES')

ADMINS = list(map(int, os.getenv('ADMINS').split(',')))                 # ID администраторов (можно хранить и в базе данных, но на старте так удобнее)
MAIN_EDITOR = list(map(int, os.getenv('MAIN_EDITOR').split(',')))       # Распределяет игроков по парам
                                                                        # Задают дивизион игрокам
                                                                        # Выдают бан
EDITOR = list(map(int, os.getenv('EDITOR').split(',')))                 # Создаёт и контролирует турнир
DIVISION_EDITOR = os.getenv('DIVISION_EDITOR')                          # Задаёт дивизион игрокам

EMAILS = list(map(str, os.getenv('EMAILS').split(',')))
DATABASE_URL = os.getenv('DATABASE_URL')
WEBAPP_URL = os.getenv('WEBAPP_URL')                                    # HTTPS-адрес Mini App (например, https://example.com)
WEBAPP_PORT = int(os.getenv('WEBAPP_PORT', '8080'))                     # Порт, на котором бот раздаёт Mini App
ADMIN_CHAT = os.getenv('ADMIN_CHAT')                                    # Чат админов для спорных моментов (если пусто — пишем каждому из ADMINS)
