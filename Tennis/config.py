import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из .env

TOKEN = os.getenv('TOKEN')
CHANNEL = os.getenv('CHANNEL')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ADMINS = list(map(int, os.getenv('ADMINS').split(',')))                 # ID администраторов (можно хранить и в базе данных, но на старте так удобнее)
MAIN_EDITOR = list(map(int, os.getenv('MAIN_EDITOR').split(',')))       # Распределяет игроков по парам
                                                                        # Задают рейтинг игрокам
                                                                        # Выдают бан
EDITOR = list(map(int, os.getenv('EDITOR').split(',')))                 # Создаёт и контролирует турнир


# PG_LINK=postgresql://USER_LOGIN:USER_PASSWORD@HOST_API:PORT/NAME_BD #Ссылка подключения к базе данных PostgreSQL   