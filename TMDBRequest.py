import requests

API_KEY = 'dd764c65e8685d30f05dddbe0f2f9e04'
BASE_URL = 'https://api.themoviedb.org/3/movie/'
BASE_URL_END = '?api_key=' + API_KEY

def get_movie_details(movie_id):
    movie_details = requests.get(BASE_URL + str(movie_id) + BASE_URL_END)
    movie_details.encoding = 'utf-8'
    if movie_details:
        return movie_details.json()

def get_movie_credits(movie_id):
    movie_credits = requests.get(BASE_URL + str(movie_id) +'/credits'+ BASE_URL_END)
    movie_credits.encoding = 'utf-8'
    if movie_credits:
        return movie_credits.json()
