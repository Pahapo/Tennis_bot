from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class MatchReward(AsyncAttrs, Base):
    __tablename__ = "match_rewards"
    id_reward = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, nullable=False)
    tg_user_id = Column(BigInteger, nullable=False)
    opponents = Column(String(60), nullable=False)    # ID соперников в виде ",id1,id2," (запятые по краям — для поиска через LIKE)
    is_win = Column(Boolean, nullable=False)
    amount = Column(Integer, nullable=False)
    counted = Column(Boolean, nullable=False)          # False — сработал лимит игр с этим соперником, монет нет
    game_date = Column(DateTime, nullable=False)


    # Конструктор __init__
    def __init__(self, match_id, tg_user_id, opponents, is_win, amount, counted, game_date):
        self.match_id = match_id
        self.tg_user_id = tg_user_id
        self.opponents = opponents
        self.is_win = is_win
        self.amount = amount
        self.counted = counted
        self.game_date = game_date
