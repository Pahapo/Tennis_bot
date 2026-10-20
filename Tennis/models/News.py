from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from config.db import Base

class News(AsyncAttrs, Base):
    __tablename__ = "news"
    id_news = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text())                       # Текст рассылки (HTML Telegram)
    photo = Column(String(100))                 # Файл фото в Tennis/img/news (если было)
    link_text = Column(String(100))             # Кнопка-ссылка из рассылки: текст
    link_url = Column(String(300))              # ... и адрес
    division = Column(Integer)                  # Рассылка только для дивизиона (None — для всех)
    date = Column(DateTime, nullable=False)


    # Конструктор __init__
    def __init__(self, date, text=None, photo=None, link_text=None, link_url=None, division=None):
        self.date = date
        self.text = text
        self.photo = photo
        self.link_text = link_text
        self.link_url = link_url
        self.division = division
