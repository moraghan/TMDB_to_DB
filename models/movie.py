from datetime import datetime

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/imdb')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Movie(Base):
    __tablename__ = 'movie'

    movie_id = Column(Integer(), primary_key=True, autoincrement=False)
    movie_title = Column(String(100), nullable=False)
    imdb_id = Column(String(20), nullable=False)
    release_date = Column(DateTime())
    runtime_mins = Column(Integer())
    budget = Column(Numeric(20, 2))
    revenue = Column(Numeric(20, 2))
    language = Column(String(5))
    overview = Column(String(1000))
    tagline = Column(String(255))
    status = Column(String(10))
    vote_average = Column(Numeric(5, 2))
    vote_count = Column(Integer())
    popularity = Column(Numeric(5, 2))
    json_request = Column(JSONB)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)


class Genre(Base):
    __tablename__ = 'genre'

    genre_id = Column(Integer(), primary_key=True, autoincrement=False)
    genre_descr = Column(String(100), nullable=False, unique=True)


class MovieGenre(Base):
    __tablename__ = 'movie_genre'

    movie_id = Column(Integer(), ForeignKey('movie.movie_id'),primary_key=True)
    genre_id = Column(Integer(), ForeignKey('genre.genre_id'),primary_key=True)


class Collection(Base):
    __tablename__ = 'collection'

    collection_id = Column(Integer(), primary_key=True, autoincrement=False)
    collection_descr = Column(String(100), nullable=False, unique=True)


class MovieCollection(Base):
    __tablename__ = 'movie_collection'

    movie_id = Column(Integer(), ForeignKey('movie.movie_id'), primary_key=True)
    collection_id = Column(Integer(), ForeignKey('collection.collection_id'), primary_key=True)


class ProductionCompany(Base):
    __tablename__ = 'production_company'

    production_company_id = Column(Integer(), primary_key=True, autoincrement=False)
    production_company_descr = Column(String(100), unique=True)
    origin_country = Column(String(5))


class MovieProductionCompany(Base):
    __tablename__ = 'movie_production_company'

    movie_id = Column(Integer(), ForeignKey('movie.movie_id'), primary_key=True)
    production_company_id = Column(Integer(), ForeignKey('production_company.production_company_id'), primary_key=True)


class ProductionCountry(Base):
    __tablename__ = 'production_country'

    production_country_code = Column(String(5), primary_key=True, autoincrement=False)
    production_country_descr = Column(String(100), unique=True)


class MovieProductionCountry(Base):
    __tablename__ = 'movie_production_country'

    movie_id = Column(Integer(), ForeignKey('movie.movie_id'), primary_key=True)
    production_country_code = Column(String(5),ForeignKey('production_country.production_country_code'), primary_key=True)

class MovieRequest(Base):
    __tablename__ = 'movie_request'

    request_id = Column(Integer(), primary_key=True, autoincrement=True)
    request_type = Column(String(20))
    request_key = Column(Integer())
    json_request = Column(JSONB)

Base.metadata.create_all(engine)
