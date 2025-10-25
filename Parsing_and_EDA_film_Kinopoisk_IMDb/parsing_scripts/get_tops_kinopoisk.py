import json
import requests

from settings import API_KEY

HEADERS = {
    'X-API-KEY': API_KEY
}

TOP_URL = "https://kinopoiskapiunofficial.tech/api/v2.2/films/collections"
FILMS_PER_PAGE = 20
MAX_PAGES = 14


def get_top_250_films_kinopoisk(type_top):
    all_films = set()
    for page in range(1, MAX_PAGES):
        params = {
            'type': type_top,
            'page': page
        }
        try:
            response = requests.get(TOP_URL, headers=HEADERS, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Ошибка при получении страницы {page}: {e}")
            continue

        data = response.json()

        films = data.get("items")
        for film in films:
            film_id = film.get('kinopoiskId')
            all_films.add(film_id)
    return all_films


types = [
    "TOP_250_MOVIES",
    "TOP_POPULAR_ALL",
    "COMICS_THEME",
    "LOVE_THEME",
    "ZOMBIE_THEME",
]
all_films_dict = {}

for top in types:
    print(top)
    films = get_top_250_films_kinopoisk(top)
    all_films_dict[top] = list(films)

    with open("../data/kinopoisk_films_by_top.json", "w", encoding="utf-8") as f:
        json.dump(all_films_dict, f, ensure_ascii=False, indent=4)

    print(f"Топ '{top}' сохранён, фильмов в топе: {len(films)}")
