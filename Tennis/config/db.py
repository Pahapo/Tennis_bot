from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config.config import DATABASE_URL

# Создаём движок
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Проверяет соединение перед использованием
    pool_recycle=1800    # Пересоздает соединения каждые 30 мин
)
# Базовый класс для моделей
Base = declarative_base()
# Создаём сессию
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

__all__ = ['Base', 'AsyncSessionLocal', 'engine']