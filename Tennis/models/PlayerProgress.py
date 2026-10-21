from sqlalchemy import Column, Integer, BigInteger, Boolean, Date, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class PlayerProgress(AsyncAttrs, Base):
    __tablename__ = "player_progress"
    tg_user_id = Column(BigInteger, primary_key=True, unique=True)
    gold = Column(Integer, nullable=False)                  # Баланс монет (можно тратить в магазине)
    season_gold = Column(Integer, nullable=False)           # Монеты, заработанные в этом году (по ним считается лига)
    season_year = Column(Integer, nullable=False)           # Год, к которому относится season_gold
    last_season_gold = Column(Integer)                      # Итог прошлого года (для экрана итогов)
    season_summary_seen = Column(Boolean)                   # Игрок уже посмотрел итоги прошлого года
    streak_days = Column(Integer, nullable=False)           # Серия заходов в приложение (дней подряд)
    best_streak = Column(Integer, nullable=False)           # Лучшая серия
    last_visit = Column(Date)                               # Дата, когда последний раз забрал ежедневную награду
    last_news_seen = Column(Integer, nullable=False)        # ID последней прочитанной новости
    skin_hero = Column(String(30))                          # Надетый герой (None — Новичок)
    skin_background = Column(String(30))                    # Надетый фон (None — стандартный корт)
    skin_racket = Column(String(30))                        # Надетая ракетка на главном экране (None — деревянная)


    # Конструктор __init__
    def __init__(self, tg_user_id, season_year, gold=0, season_gold=0, last_season_gold=None, season_summary_seen=True, streak_days=0, best_streak=0, last_visit=None, last_news_seen=0, skin_hero=None, skin_background=None, skin_racket=None):
        self.tg_user_id = tg_user_id
        self.season_year = season_year
        self.gold = gold
        self.season_gold = season_gold
        self.last_season_gold = last_season_gold
        self.season_summary_seen = season_summary_seen
        self.streak_days = streak_days
        self.best_streak = best_streak
        self.last_visit = last_visit
        self.last_news_seen = last_news_seen
        self.skin_hero = skin_hero
        self.skin_background = skin_background
        self.skin_racket = skin_racket
