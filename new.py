from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from models.movie import Movie
from models.movie import MovieGenre
from models.movie import MovieProductionCompany
from models.movie import MovieCollection
from models.movie import MovieProductionCountry
from models.movie import Genre
from models.movie import ProductionCompany
from models.movie import ProductionCountry
from models.movie import Collection


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

Base.metadata.create_all(engine)

# response = requests.get('https://api.themoviedb.org/3/movie/285?api_key=' + API_KEY)

for movie_id in range(1, 1490):

    print('Retrieving movie details:', movie_id)

    try:

        movie = TMDBRequest.get_movie_details(movie_id)

        if movie:
            save_movie_details(movie)
            session.commit()

    except Exception as e:
        print("Failed trying to return information for:", e)
        raise e

    finally:

        session.close()
