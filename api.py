import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_LONG_KEY = os.getenv("API_LONG_KEY")
api_key = API_KEY
api_long_key = API_LONG_KEY
url = f"https://api.themoviedb.org/3/authentication"
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {api_long_key}",
}


# response = requests.get(url, headers=headers)

#
# url_searsh = "https://api.themoviedb.org/3/search/movie"
# params = {
#     "query": "Inception",
#     # "api_key": api_key,
#     "language": "en-US",
#     "page": 1,
#     "include_adult": True,
# }
#
# response_search = requests.get(url_searsh, headers=headers, params=params)
# data = response_search.json()
# print(data)


def search_movies(title: str):
    url_searsh = "https://api.themoviedb.org/3/search/movie"
    params = {
        "query": title,
        # "api_key": api_key,
        "language": "en-US",
        "page": 1,
        "include_adult": True,
    }

    response_search = requests.get(url_searsh, headers=headers, params=params)
    data = response_search.json()
    movies_list = []
    movie_id_list = []
    for title in data["results"]:
        movies_list.append(f"{title['title']} -  {title['release_date']}")
        movie_id_list.append(title["id"])
    return (movies_list, movie_id_list)


def movie_data(id):
    url_movie = f"https://api.themoviedb.org/3/movie/{id}"
    response_movie = requests.get(url_movie, headers=headers)
    data = response_movie.json()
    title = data["original_title"]
    release_date = data["release_date"]
    overview = data["overview"]
    img_url = data["backdrop_path"]
    return (title, release_date, overview, img_url)

# print(movie_data("109445"))
