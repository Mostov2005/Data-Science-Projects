import re
from camoufox.sync_api import Camoufox
from bs4 import BeautifulSoup
from time import sleep
from settings import *


def clean_price(raw_price: str):
    """Очистка и преобразование цены в float"""

    if raw_price is None:
        return None

    cleaned = raw_price.replace("\xa0", " ").strip()
    cleaned = re.sub(r"[^\d.,]", "", cleaned)  # удаляем всё, кроме чисел и знаков
    cleaned = cleaned.replace(",", ".")

    try:
        return float(cleaned)
    except ValueError:
        return cleaned


def get_udemy_course_info(url: str, locale="ru-RU", headless=False, difficulty="Все уровни"):
    """
    Парсит страницу курса Udemy и возвращает словарь с данными.
    """

    proxy_settings = {
        "server": server,
        "username": username,
        "password": password
    }
    difficulty = difficulty

    with Camoufox(
            geoip=True,
            proxy=proxy_settings,
            os="windows",
            locale=locale,
            headless=True
    ) as browser:
        page = browser.new_page()
        page.goto(url, timeout=120000)
        sleep(10)  # ждём прогрузку JS

        soup = BeautifulSoup(page.content(), "html.parser")

        # Название
        title_elem = soup.select_one('h1[data-purpose="lead-title"]')
        title = title_elem.get_text(strip=True) if title_elem else None

        # Описание
        description_elem = soup.select_one('div[data-purpose="lead-headline"]')
        description = description_elem.get_text(strip=True) if description_elem else None

        # Сертификат
        certificate_elem = soup.select_one('span[data-purpose="incentive-certificate"]')
        certificate_available = certificate_elem is not None

        # Рейтинг
        rating_elem = soup.select_one('span[data-purpose="rating-number"]')
        rating = rating_elem.get_text(strip=True) if rating_elem else None

        # Количество отзывов
        reviews_elem = soup.select_one('a[data-purpose="rating"] span:nth-of-type(2)')
        reviews_count = reviews_elem.get_text(strip=True) if reviews_elem else None

        # Количество студентов
        students_elem = soup.select_one('div[data-purpose="enrollment"]')
        students = students_elem.get_text(strip=True) if students_elem else None

        # Цена
        price_elem = soup.select_one('div[data-purpose="course-price-text"] span span')
        raw_price = price_elem.get_text(strip=True) if price_elem else None
        price = clean_price(raw_price)

        browser.close()

    index = url.split("course/")[1]

    # Финальный словарь
    return {
        "index": index,
        "title": title,
        "description": description,
        "certificate_available": certificate_available,
        "difficulty": difficulty,
        "rating": rating,
        "reviews_count": reviews_count,
        "price": price,
        "students": students,
        "source": "udemy",
        "course": "Обработка и анализ данных"
    }


def get_result(url: str, difficulty="Все уровни", retries=3):
    fields = [
        "index", "title", "description", "difficulty",
        "certificate_available", "students", "price",
        "rating", "reviews_count", "source", "course"
    ]

    # Итоговый словарь с None
    data = {f: None for f in fields}

    for attempt in range(retries + 1):
        try:
            current = get_udemy_course_info(url, difficulty=difficulty)
            for key in fields:
                if data.get(key) is None and current.get(key) is not None:
                    data[key] = current[key]

            if None not in data.values():
                return data

        except Exception as e:
            print(f"Ошибка попытки #{attempt} для {url}: {e}")

        sleep(0.2)

    return data
