import time
import json
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from settings import API_KEY


HEADERS = {
    'X-API-KEY': API_KEY
}

FILM_URL_KINOPOISK = 'https://kinopoiskapiunofficial.tech/api/v2.2/films/'
FILMS_PER_PAGE = 20
MAX_PAGES = 14


def parse_film_imdb(link):
    url = link
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Название
    try:
        title = soup.find('span', class_='hero__primary-text').text.strip()
    except:
        title = ""

    # Год
    try:
        year = soup.select_one('a[href*="/releaseinfo/"]').text.strip()
    except:
        year = ""

    # Рейтинг
    try:
        rating = soup.select_one('div[data-testid="hero-rating-bar__aggregate-rating__score"] span').text.strip()
    except:
        rating = ""

    # Возрастной лимит
    try:
        age_limit = soup.select_one('a[href*="parentalguide"]').text.strip()
    except:
        age_limit = ""

    # Жанры
    genres = []
    try:
        genre_block = soup.select_one('section div.ipc-chip-list__scroller')
        if genre_block:
            for chip in genre_block.find_all('span', class_='ipc-chip__text'):
                genres.append(chip.text.strip())
    except:
        pass
    genres_str = ", ".join(genres)

    # Страна
    try:
        country = soup.select_one('a[href*="country_of_origin"]').text.strip()
    except:
        country = ""

    # Режиссёр
    try:
        director = soup.select_one('a[href*="name"]').text.strip()
    except:
        director = ""

    # Бюджет
    try:
        budget_raw = soup.select_one(
            'li[data-testid="title-boxoffice-budget"] '
            'span.ipc-metadata-list-item__list-content-item'
        ).text.strip()
        budget = int(re.sub(r'\D', '', budget_raw))
    except:
        budget = 0

    # Сборы
    try:
        fees_raw = soup.select_one(
            'li[data-testid="title-boxoffice-cumulativeworldwidegross"] '
            'span.ipc-metadata-list-item__list-content-item.ipc-btn--not-interactable'
        ).text.strip()
        fees = int(re.sub(r'\D', '', fees_raw))
    except:
        fees = 0

    # Описание
    try:
        description = soup.select_one('span[data-testid="plot-xl"]').text.strip()
    except:
        description = ""

    data = [
        title,
        year,
        rating,
        age_limit,
        genres_str,
        country,
        director,
        budget,
        fees,
        description
    ]

    return data


def get_info_film_kinopoisk(id_film):
    FILM_URL = f"{FILM_URL_KINOPOISK}{id_film}"
    try:
        response = requests.get(FILM_URL, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при получении страницы: {e}")
        return

    data = response.json()

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
        'age': str(age).replace('age', '') + '+' if age else 'N/A',
        'genres': ', '.join(genres) if genres else 'N/A',
        'countries': ', '.join(countries) if countries else 'N/A',
        'description': description.replace("\xa0", " ") if description else 'N/A'
    }


# df = pd.DataFrame({
#     "Title": [],
#     'kinopoiskId': [],
#     'imdbId': [],
#     "Year": [],
#     "Rating Kinopoisk": [],
#     "Rating Imdb": [],
#     "Age Limit": [],
#     "Genres": [],
#     "Country": [],
#     "Director": [],
#     "Budget $": [],
#     "Fees $": [],
#     "Description Kinopoisk": [],
#     "Description Imdb": []
# })

with open("../data/kinopoisk_films_by_top.json", "r", encoding="utf-8") as f:
    all_films_dict = json.load(f)

all_ids = set()
for films in all_films_dict.values():
    all_ids.update(films)

df = pd.read_csv('../data/data_films.csv')
df["kinopoiskId"] = df["kinopoiskId"].astype(int)
ready_id = set(df["kinopoiskId"])

c = 0
for id_film in all_ids:
    if id_film in ready_id:
        continue
    data_kinopoisk = get_info_film_kinopoisk(id_film=id_film)
    imdbId = data_kinopoisk['imdbId']

    if not imdbId:
        continue

    url_imdb = f'https://www.imdb.com/title/{imdbId}'
    data_imdb = parse_film_imdb(url_imdb)
    row = {
        "Title": data_kinopoisk['name'],
        'kinopoiskId': data_kinopoisk['kinopoiskId'],
        'imdbId': data_kinopoisk['imdbId'],
        "Year": data_kinopoisk['year'],
        "Rating Kinopoisk": data_kinopoisk['rating'],
        "Rating Imdb": data_imdb[2],
        "Age Limit": data_kinopoisk['age'],
        "Genres": data_kinopoisk['genres'],
        "Country": data_kinopoisk['countries'],
        "Director": data_imdb[6],
        "Budget $": data_imdb[7],
        "Fees $": data_imdb[8],
        "Description Kinopoisk": data_kinopoisk['description'],
        "Description Imdb": data_imdb[9]
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv("data_films.csv", index=False, encoding="utf-8-sig")
    c += 1
    print(c)
    time.sleep(0.3)
