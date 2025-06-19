from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.config import DATABASE_URL

# Создаём движок
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Проверяет соединение перед использованием
    pool_recycle=1800    # Пересоздает соединения каждые 30 мин
)
# Базовый класс для моделей
Base = declarative_base()
# Создаём сессию
Session = sessionmaker(bind=engine)
session = Session()