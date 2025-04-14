from sqlalchemy import Column, Integer, String, Boolean, BigInteger
from config.db import Base

class User(Base):
    __tablename__ = "users"
    tg_user_id = Column(BigInteger, primary_key=True, unique=True)
    name_user = Column(String(20), nullable=True)
    link = Column(String(30), nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String(10), nullable=True)
    division_level = Column(Integer)
    ban_status = Column(Boolean)
    end_date_ban = Column(String(10))


    # Конструктор __init__
    def __init__(self, tg_user_id, name_user, link, age=None, sex=None, division_level=None, ban_status=None, end_date_ban=None):
        self.tg_user_id = tg_user_id
        self.name_user = name_user
        self.link = link
        self.age = age
        self.sex = sex
        self.division_level = division_level
        self.ban_status = ban_status
        self.end_date_ban = end_date_ban


    def __repr__(self):
        return f"Имя: {self.name_user}\nВозраст: {self.age}\nПол: {self.sex}\nУровень игры: {self.division_level}\nНаличие бана: {self.ban_status} (До {self.end_date_ban})\n" 
        #  История турниров: {self.tournaments_list}