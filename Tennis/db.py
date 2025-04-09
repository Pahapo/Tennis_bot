from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:valeriaSQL13@localhost/tennisDB"

# Создаём движок
engine = create_engine(DATABASE_URL)
# Базовый класс для моделей
Base = declarative_base()
# Создаём сессию
Session = sessionmaker(bind=engine)
session = Session()