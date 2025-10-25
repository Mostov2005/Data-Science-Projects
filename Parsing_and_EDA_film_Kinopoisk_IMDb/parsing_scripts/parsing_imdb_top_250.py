from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup


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
        rating = soup.select_one('span.sc-d541859f-1.imUuxf').text.strip()
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
        description = soup.select_one('span.sc-e32edc92-0.jmIYOm').text.strip()
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


def get_urls_imdb():
    options = Options()
    options.add_argument('--headless')
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                 "AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/115.0.0.0 Safari/537.36"
    options.add_argument(f'user-agent={user_agent}')

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.imdb.com/chart/top/")

    movie_links = driver.find_elements(By.CSS_SELECTOR, 'a.ipc-title-link-wrapper')

    urls = []
    for link in movie_links:
        href = link.get_attribute('href')
        if href and '/title/tt' in href:
            urls.append(href.split('?')[0])

    driver.quit()
    return urls


urls_imdb = get_urls_imdb()
print(urls_imdb)
df = pd.DataFrame({
    "Title": [],
    "Year": [],
    "Rating": [],
    "Age Limit": [],
    "Genres": [],
    "Country": [],
    "Director": [],
    "Budget": [],
    "Fees": [],
    "Description": []
})

c = 0
for url in urls_imdb:
    data_film = parse_film_imdb(url)
    df.loc[len(df)] = data_film
    df.to_csv("imdb_films.csv", index=False, encoding="utf-8-sig")
    c += 1
    print(c)
