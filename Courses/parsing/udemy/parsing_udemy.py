import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

from bs4 import BeautifulSoup
from camoufox.sync_api import Camoufox

from settings import *


def get_udemy_courses(url, locale="ru-RU"):
    """
    Получает список курсов с Udemy с их ссылками и сложностью.
    """
    courses_data = []

    proxy_settings = {
        "server": server,
        "username": username,
        "password": password
    }

    with Camoufox(geoip=True,
                  proxy=proxy_settings,
                  os="windows",
                  locale=locale,
                  headless=True) as browser:
        page = browser.new_page()
        page.goto(url, timeout=120000)
        sleep(10)

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Находим все h3 с ссылками на курс
        for h3_tag in soup.select('h3[data-purpose="course-title-url"]'):
            a_tag = h3_tag.find('a')
            if a_tag and a_tag.get('href', '').startswith("/course/"):
                href = a_tag['href']

                # Ищем блок с info о курсе
                meta_info_div = h3_tag.find_next('div', attrs={'data-purpose': 'course-meta-info'})
                complexity = None
                if meta_info_div:
                    spans = meta_info_div.find_all('span')
                    if spans:
                        complexity = spans[-1].get_text(strip=True)
                if complexity is None or href is None:
                    continue
                courses_data.append({
                    "url": href,
                    "complexity": complexity
                })

        browser.close()

    unique_courses = [dict(t) for t in {tuple(d.items()) for d in courses_data}]
    return unique_courses


all_data = {}
max_workers = 5  # количество потоков

def process_page(page):
    url = f"https://www.udemy.com/courses/development/data-science/?lang=en&lang=ru&p={page}&price=price-paid&sort=most-reviewed"
    courses = get_udemy_courses(url)
    print(f"Страница {page} сохранена. Курсов: {len(courses)}")
    return page, courses

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(process_page, page) for page in range(1, 166)]

    for future in as_completed(futures):
        page, courses = future.result()
        all_data[page] = courses

        with open("udemy_pages.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
