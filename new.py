from datetime import datetime

from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy import DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import TMDBRequest

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost:5432/imdb')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


def save_movie_details(movie_json: dict):
    if session.query(Movie).filter(Movie.movie_id == movie_json['id']).first() is None:
        movie_to_add = Movie(

            movie_id=movie_json['id'],
            movie_title=movie_json['title'],
            imdb_id=movie_json['imdb_id'],
            release_date=movie_json['release_date'] or None,
            runtime_mins=movie_json['runtime'],
            budget=movie_json['budget'] or None,
            revenue=movie_json['revenue'] or None,
            language=movie_json['original_language'],
            overview=movie_json['overview'],
            tagline=movie_json['tagline'],
            status=movie_json['status'],
            vote_average=movie_json['vote_average'],
            vote_count=movie_json['vote_count'],
            popularity=movie_json['popularity']

        )
        session.add(movie_to_add)

    for genre in movie_json['genres']:

        if session.query(Genre).filter(Genre.genre_id == genre['id']).first() is None:
            genre_to_add = Genre(
                genre_id=genre['id'],
                genre_descr=genre['name']
            )

            session.add(genre_to_add)

        if session.query(MovieGenre).filter(MovieGenre.movie_id == movie_json['id'],
                                            MovieGenre.genre_id == genre['id']).first() is None:
            movie_genre_to_add = MovieGenre(
                movie_id=movie_json['id'],
                genre_id=genre['id']
            )

            session.add(movie_genre_to_add)

        for production_company in movie_json['production_companies']:

            existing_production_company = session.query(ProductionCompany).filter(
                ProductionCompany.production_company_descr == production_company['name']).first()

            if existing_production_company is None:

                production_company_to_add = ProductionCompany(
                    production_company_id=production_company['id'],
                    production_company_descr=production_company['name'],
                    origin_country=production_company['origin_country']
                )

                session.add(production_company_to_add)
                production_company_id = production_company['id']
            else:
                production_company_id = existing_production_company.production_company_id

            movie_production_company_to_add = MovieProductionCompany(
                movie_id=movie_json['id'],
                production_company_id=production_company_id
            )

            if session.query(MovieProductionCompany).filter(MovieProductionCompany.movie_id == movie_json['id'],
                                                            MovieProductionCompany.production_company_id ==
                                                            production_company_id).first() is None:
                session.add(movie_production_company_to_add)

            for production_country in movie_json['production_countries']:

                if session.query(ProductionCountry).filter(
                        ProductionCountry.production_country_code == production_country['iso_3166_1']).first() is None:
                    production_country_to_add = ProductionCountry(
                        production_country_code=production_country['iso_3166_1'],
                        production_country_descr=production_country['name']
                    )
                    session.add(production_country_to_add)

                if session.query(MovieProductionCountry).filter(MovieProductionCountry.movie_id == movie_json['id'],
                                                                MovieProductionCountry.production_country_code ==
                                                                production_country['iso_3166_1']).first() is None:
                    movie_production_country_to_add = MovieProductionCountry(
                        movie_id=movie_json['id'],
                        production_country_code=production_country['iso_3166_1']
                    )
                    session.add(movie_production_country_to_add)

    return 0


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

# response = requests.get('https://api.themoviedb.org/3/movie/285?api_key=' + API_KEY)

for movie_id in range(1, 1490):

    print('Retrieving movie details:', movie_id)

    try:

        # response = requests.get(BASE_URL + str(movie_id) + BASE_URL_END)

        # movie = response.json()

        movie = TMDBRequest.get_movie_details(movie_id)

        if movie:
            save_movie_details(movie)
            session.commit()

    except Exception as e:
        print("Failed trying to return information for:", e)
        raise e

    finally:

        session.close()
