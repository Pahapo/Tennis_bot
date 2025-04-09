from sqlalchemy import Column, Integer, String
from db import Base

class User(Base):
    __tablename__ = "users"
    tg_user_id = Column(Integer, primary_key=True, unique=True)
    name_user = Column(String(20), nullable=False)
    link = Column(String(30), nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String(10), nullable=False)
    division_level = Column(Integer)
    ban_status = Column(Integer)
    end_date_ban = Column(String(10))


    # Конструктор __init__
    def __init__(self, tg_user_id, name_user, link, age, sex, division_level, ban_status, end_date_ban):
        self.tg_user_id = tg_user_id
        self.name_user = name_user
        self.link = link
        self.age = age
        self.sex = sex
        self.division_level = division_level
        self.ban_status = ban_status
        self.end_date_ban = end_date_ban


    def __repr__(self):
        return f"Имя: {self.name_user}\nВозраст: {self.age}\nПол: {self.sex}\n" 
        # "История турниров": self.end_date_ban,
        # "Предпочтительное время игры": self.end_date_ban