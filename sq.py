from datetime import datetime

import requests
from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy import DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/imdb')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

API_KEY = 'dd764c65e8685d30f05dddbe0f2f9e04'
BASE_URL = 'https://api.themoviedb.org/3/movie/'
BASE_URL_END = '?api_key=' + API_KEY


class Movie(Base):
    __tablename__ = 'movie'

    movie_id = Column(Integer(), primary_key=True)
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
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)


class Genre(Base):
    __tablename__ = 'genre'

    genre_id = Column(Integer(), primary_key=True)
    genre_descr = Column(String(100), nullable=False, unique=True)


class MovieGenre(Base):
    __tablename__ = 'movie_genre'

    movie_id = Column(Integer(), primary_key=True)
    genre_id = Column(Integer(), primary_key=True)


class Collection(Base):
    __tablename__ = 'collection'

    collection_id = Column(Integer(), primary_key=True)
    collection_descr = Column(String(100), nullable=False, unique=True)


class MovieCollection(Base):
    __tablename__ = 'movie_collection'

    movie_id = Column(Integer(), primary_key=True)
    collection_id = Column(Integer(), primary_key=True)

class ProductionCompany(Base):
    __tablename__ = 'production_company'

    production_company_id = Column(Integer(), primary_key=True)
    production_company_descr = Column(String(100), unique=True)
    origin_country = Column(String(5))

class MovieProductionCompany(Base):
    __tablename__ = 'movie_production_company'

    movie_id = Column(Integer(), primary_key=True)
    production_company_id = Column(Integer(), primary_key=True)

class ProductionCountry(Base):
    __tablename__ = 'production_country'

    production_country_code = Column(String(5), primary_key=True)
    production_country_descr = Column(String(100), unique=True)

class MovieProductionCountry(Base):
    __tablename__ = 'movie_production_country'

    movie_id = Column(Integer(), primary_key=True)
    production_country_code = Column(String(5), primary_key=True)

Base.metadata.create_all(engine)

response = requests.get('https://api.themoviedb.org/3/movie/285?api_key=' + API_KEY)

for movie_id in range(658, 660):

    print('Retrieving movie details:', movie_id)

    try:

        response = requests.get(BASE_URL + str(movie_id) + BASE_URL_END)

        movie = response.json()
        print(movie.status_code)

        movie_to_add = Movie(

            movie_id=movie['id'],
            movie_title=movie['title'],
            imdb_id=movie['imdb_id'],
            release_date=movie['release_date'],
            runtime_mins=movie['runtime'],
            budget=movie['budget'] or None,§ 
            revenue=movie['revenue'] or None,
            language=movie['original_language'],
            overview=movie['overview'],
            tagline=movie['tagline'],
            status=movie['status'],
            vote_average=movie['vote_average'],
            vote_count=movie['vote_count'],
            popularity=movie['popularity']

        )

        if session.query(Movie).filter(Movie.movie_id == movie['id']).first() is None:
            session.add(movie_to_add)

        for genre in movie['genres']:

            genre_to_add = Genre(
                genre_id=genre['id'],
                genre_descr=genre['name']
            )

            if session.query(Genre).filter(Genre.genre_id == genre['id']).first() is None:
                session.add(genre_to_add)

            movie_genre_to_add = MovieGenre(
                movie_id=movie['id'],
                genre_id=genre['id']
            )

            if session.query(MovieGenre).filter(MovieGenre.movie_id == movie['id'],
                                                MovieGenre.genre_id == genre['id']).first() is None:
                session.add(movie_genre_to_add)

            for production_company in movie['production_companies']:

                production_company_to_add = ProductionCompany(
                    production_company_id=production_company['id'],
                    production_company_descr=production_company['name'],
                    origin_country=production_company['origin_country']
                )

                if session.query(ProductionCompany).filter(ProductionCompany.production_company_id == production_company['id']).first() is None:
                    session.add(production_company_to_add)

                movie_production_company_to_add = MovieProductionCompany(
                    movie_id=movie['id'],
                    production_company_id=production_company['id']
                )

                if session.query(MovieProductionCompany).filter(MovieProductionCompany.movie_id == movie['id'],
                                                    MovieProductionCompany.production_company_id == production_company['id']).first() is None:
                    session.add(movie_production_company_to_add)

                for production_country in movie['production_countries']:

                    production_country_to_add = ProductionCountry(
                        production_country_code=production_country['iso_3166_1'],
                        production_country_descr=production_country['name']
                    )

                    if session.query(ProductionCountry).filter(
                            ProductionCountry.production_country_code == production_country['iso_3166_1']).first() is None:
                        session.add(production_country_to_add)

                    movie_production_country_to_add = MovieProductionCountry(
                        movie_id=movie['id'],
                        production_country_code=production_country['iso_3166_1']
                    )

                    if session.query(MovieProductionCountry).filter(MovieProductionCountry.movie_id == movie['id'],
                                        MovieProductionCountry.production_country_code == production_country['iso_3166_1']).first() is None:
                        session.add(movie_production_country_to_add)

        session.commit()

    except Exception as e:
        print("Failed trying to return information for:", e)

    finally:

        session.close()



def get_movie_details(Movie)-> Movie:
    return Movie