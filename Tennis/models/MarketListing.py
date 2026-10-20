from sqlalchemy import Column, Integer, BigInteger, Float, String, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class MarketListing(AsyncAttrs, Base):
    __tablename__ = "market_listings"
    id_listing = Column(Integer, primary_key=True, autoincrement=True)
    tg_user_id = Column(BigInteger, nullable=False)        # Продавец
    title = Column(String(60), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)                  # бел.руб.
    category = Column(String(30), nullable=False)
    item_condition = Column(String(20), nullable=False)    # Новое / Б/у
    photos = Column(String(300), nullable=False)           # Файлы в Tennis/img/market через запятую
    status = Column(String(20), nullable=False)            # moderation, active, rejected, sold, deleted
    created = Column(DateTime, nullable=False)
    expires = Column(DateTime)                             # До какого числа видно (после одобрения — 30 дней)


    # Конструктор __init__
    def __init__(self, tg_user_id, title, description, price, category, item_condition, photos, created, status='moderation', expires=None):
        self.tg_user_id = tg_user_id
        self.title = title
        self.description = description
        self.price = price
        self.category = category
        self.item_condition = item_condition
        self.photos = photos
        self.created = created
        self.status = status
        self.expires = expires
