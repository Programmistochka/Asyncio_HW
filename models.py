import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import JSON, Integer, String, Column

PG_USER=os.getenv('PG_USER', 'postgres')
PG_PASSWORD=os.getenv('PG_PASSWORD', 'postgres')
PG_DB=os.getenv('PG_DB', 'asyncio_test')
PG_HOST=os.getenv('PG_HOST', '127.0.0.1')
PG_PORT=os.getenv('PG_PORT', '5432') #Для запуска лок БД - 5432, для Docker контейнера с БД - 5431

PG_DSN = f'postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'
engine = create_async_engine(PG_DSN)   # создание асинхронного движка
Base = declarative_base()              # фабрика
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False) # базовый клсс для сессии 
                                                                                 # настройка expire_on_commit=False - чтобы сессия не истекала


class SwapiPeople(Base):
    __tablename__ = 'swapi_people'
    id = Column(Integer, primary_key=True)
    json = Column(JSON)
    # Все данные содержатся в поле json
    # name = Column(String)
    # birth_year = Column(String)
    # eye_color = Column(String)
    # films = Column(String) # строка с названиями фильмов через запятую
    # gender = Column(String)
    # hair_color = Column(String)
    # height = Column(String)
    # homeworld = Column(String)
    # mass = Column(String)   
    # skin_color = Column(String)
    # species = Column(String) # строка с названиями типов через запятую
    # starships = Column(String) # строка с названиями кораблей через запятую
    # vehicles = Column(String)