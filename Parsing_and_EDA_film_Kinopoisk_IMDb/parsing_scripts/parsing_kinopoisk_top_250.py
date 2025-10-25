import requests
import pandas as pd
from settings import API_KEY


HEADERS = {
    'X-API-KEY': API_KEY
}

TOP_250_URL = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/top'
FILM_URL = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/'
FILMS_PER_PAGE = 20
MAX_PAGES = 14


def get_top_250_films_kinopoisk():
    all_films = set()
    for page in range(1, MAX_PAGES):
        params = {
            'type': 'TOP_250_BEST_FILMS',
            'page': page
        }
        try:
            response = requests.get(TOP_250_URL, headers=HEADERS, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Ошибка при получении страницы {page}: {e}")
            continue

        data = response.json()
        films = data.get('films', [])

        for film in films:
            film_id = film.get('filmId')
            all_films.add(film_id)

    return all_films


def get_info_film_kinopoisk(id_film):
    FILM_URL = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{id_film}"
    try:
        response = requests.get(FILM_URL, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при получении страницы: {e}")
        return

    data = response.json()
    # pprint(data)

    kinopoiskId = data.get('kinopoiskId')
    imdbId = data.get('imdbId')
    name = data.get('nameRu') or data.get('nameEn') or 'Без названия'
    year = data.get('year', 'N/A')
    rating = data.get('ratingKinopoisk', 'N/A')
    age = data.get('ratingAgeLimits', 'N/A')
    description = data.get('description', 'Нет описания')

    genres = [g['genre'] for g in data.get('genres', [])]
    countries = [c['country'] for c in data.get('countries', [])]

    return {
        'kinopoiskId': kinopoiskId,
        'imdbId': imdbId,
        'name': name,
        'year': year,
        'rating': rating,
        'age': age.replace('age', '') + '+' if age else 'N/A',
        'genres': ', '.join(genres),
        'countries': ', '.join(countries),
        'description': description.replace("\xa0", " ")
    }


df = pd.DataFrame({
    "Title": [],
    "Year": [],
    "Rating Kinopoisk": [],
    "Rating Imdb": [],
    "Age Limit": [],
    "Genres": [],
    "Country": [],
    "Director": [],
    "Budget": [],
    "Fees": [],
    "Description Kinopoisk": [],
    "Description Imdb": []
})

id_films = get_top_250_films_kinopoisk()
print(len(id_films))
c = 0
for id_film in id_films:
    c += 1
    print(c)
    data_film = get_info_film_kinopoisk(id_film=id_film)
    print(data_film)
    break
