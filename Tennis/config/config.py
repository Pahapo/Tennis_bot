import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env

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