import psycopg2
import requests

conn = psycopg2.connect(
    host="localhost",
    database="imdb",
    user="postgres",
    password="postgres")

API_KEY = 'dd764c65e8685d30f05dddbe0f2f9e04'
BASE_URL = 'https://api.themoviedb.org/3/movie/'
BASE_URL_END = '?api_key=' + API_KEY

movie_insert_sql = """ 
insert into mv (movie_id, movie_title, imdb_id, release_date, runtime_mins, budget, revenue, language, overview, tagline, status, vote_average, vote_count, popularity) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

genre_insert_sql = """ 
insert into genre (genre_id, genre_desc) select %s, %s where not exists (select 1 from genre where genre_id = %s);
"""

movie_genre_insert_sql = """ 
insert into mv_genre (movie_id, genre_id) select %s, %s where not exists (select 1 from mv_genre where movie_id = %s and genre_id = %s);
"""

cur = conn.cursor()

response = requests.get('https://api.themoviedb.org/3/movie/285?api_key=' + API_KEY)

for movie_id in range(100, 3000):

    print('Retrieving movie details:', movie_id)

    try :

        response = requests.get(BASE_URL + str(movie_id) + BASE_URL_END )

        movie = response.json()

        movie_details = (movie['id'],
                         movie['title'],
                         movie['imdb_id'],
                         movie['release_date'],
                         movie['runtime'],
                         movie['budget'] or None,
                         movie['revenue'] or None,
                         movie['original_language'],
                         movie['overview'],
                         movie['tagline'],
                         movie['status'],
                         movie['vote_average'],
                         movie['vote_count'],
                         movie['popularity']
                         )

        for genre in movie['genres']:
            genre_details = (genre['id'],
                             genre['name'],
                             genre['id']
                             )

            movie_genre_details = (movie['id'],
                                   genre['id'],
                                   movie['id'],
                                   genre['id']
                                   )

            cur.execute(genre_insert_sql, genre_details)

            SQL = "INSERT INTO " + "genre" + " SELECT " + str(genre['id']) + ",'" + genre['name'] + "'"
            print(SQL)
            cur.execute(SQL)
            cur.execute(movie_genre_insert_sql, movie_genre_details)

        cur.execute(movie_insert_sql, movie_details)

        conn.commit()

    except:
        print("Failed trying to return information for:", movie_id)

conn.close()
