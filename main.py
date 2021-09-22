import psycopg2
import tmdbsimple as tmdb

conn = psycopg2.connect(
    host="localhost",
    database="imdb",
    user="postgres",
    password="postgres")

cur = conn.cursor()

tmdb.API_KEY = 'dd764c65e8685d30f05dddbe0f2f9e04'

movie_insert_sql = """ 
insert into mv (movie_id, movie_title, imdb_id, release_date, runtime_mins, budget, revenue, language, overview, tagline, status, vote_average, vote_count, popularity) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

genre_insert_sql = """ 
insert into genre (genre_id, genre_desc) select %s, %s where not exists (select 1 from genre where genre_id = %s);
"""

movie_genre_insert_sql = """ 
insert into mv_genre (movie_id, genre_id) select %s, %s where not exists (select 1 from mv_genre where movie_id = %s and genre_id = %s);
"""

for movie_id in range(10000, 19672):
    print('Retrieving information for movie id:', movie_id)
    movie = tmdb.Movies(movie_id)
    try:
        r2 = movie.info()

        if movie.budget == 0:
            budget = None
        else:
            budget = movie.budget

        if movie.revenue == 0:
            revenue = None
        else:
            revenue = movie.revenue

        movie_details = (movie.id,
                         movie.title,
                         movie.imdb_id,
                         movie.release_date,
                         movie.runtime,
                         budget,
                         revenue,
                         movie.original_language,
                         movie.overview,
                         movie.tagline,
                         movie.status,
                         movie.vote_average,
                         movie.vote_count,
                         movie.popularity
                         )

        for genre in movie.genres:
            genre_details = (genre['id'],
                             genre['name'],
                             genre['id']
                             )

            cur.execute(genre_insert_sql, genre_details)

            movie_genre_details = (movie.id,
                                   genre['id'],
                                   movie.id,
                                   genre['id']
                                   )

            cur.execute(movie_genre_insert_sql, movie_genre_details)

        cur.execute(movie_insert_sql, movie_details)

        conn.commit()

    except:
        print("Failed trying to return information for:", movie_id)

conn.close()

# r = movie.credits()
# for m in movie.cast:
#     print(m['id'], m['name'], m['character'])
