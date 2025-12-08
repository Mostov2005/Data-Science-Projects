import time

import requests
import json
from bs4 import BeautifulSoup
from typing import Optional, Dict
from pprint import pprint
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
import time
from settings import proxy_ip_port
from settings import username
from settings import password


class StepikCourseParser:
    BASE_URL = "https://stepik.org/course/"

    def __init__(self, index: int):
        self.url = f'{self.BASE_URL}{index}'
        self.index = index
        self.html: Optional[str] = None
        self.soup: Optional[BeautifulSoup] = None

        self.proxy_ip_port = proxy_ip_port
        self.username = username
        self.password = password

    def fetch_requests(self, headers: Optional[Dict[str, str]] = None) -> None:
        """
        Делает HTTP-GET запрос и сохраняет HTML.
        """
        try:
            resp = requests.get(self.url, headers=headers, timeout=10)
            resp.raise_for_status()
            self.html = resp.text

        except Exception as e:
            print(e)

    def fetch_selenium(self, wait_time: int = 3) -> None:
        """
        Загружает страницу через Selenium и сохраняет HTML, используя прокси с аутентификацией.
        :param wait_time: Время ожидания подгрузки JS-контента (секунды)
        """
        try:
            proxy_ip_port = self.proxy_ip_port
            username = self.username
            password = self.password

            # Опции Chrome
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

            # Настройки selenium-wire для прокси с логином/паролем
            seleniumwire_options = {
                'proxy': {
                    'http': f'http://{username}:{password}@{proxy_ip_port}',
                    'https': f'https://{username}:{password}@{proxy_ip_port}',
                    'no_proxy': 'localhost,127.0.0.1'
                }
            }

            service = Service()
            driver = webdriver.Chrome(service=service, options=options, seleniumwire_options=seleniumwire_options)

            driver.get(self.url)
            time.sleep(wait_time)

            self.html = driver.page_source
            driver.quit()

        except Exception as e:
            print(f"Ошибка при загрузке страницы: {e}")

    def parse(self) -> None:
        """
        Разбирает HTML с помощью BeautifulSoup.
        """
        if self.html is None:
            raise RuntimeError("HTML not fetched. Call fetch() first.")

        self.soup = BeautifulSoup(self.html, "html.parser")
        # print(self.soup)

    def get_title(self) -> Optional[str]:
        """
        Возвращает заголовок курса (если есть).
        """
        if self.soup is None:
            raise RuntimeError("Soup not prepared. Call parse() first.")
        title_tag = self.soup.find("h1")
        if title_tag:
            return title_tag.get_text(strip=True)
        if self.soup.title:
            return self.soup.title.get_text(strip=True)
        return None

    def get_description(self) -> Optional[str]:
        """
        Возвращает описание курса из meta[name="description"] или og:description.
        """
        if self.soup is None:
            raise RuntimeError("Soup not prepared. Call parse() first.")

        # meta[name="description"]
        tag = self.soup.find("meta", attrs={"name": "description"})
        if tag and tag.get("content"):
            return tag["content"].replace("\n", " ").strip()

        # meta[property="og:description"]
        tag = self.soup.find("meta", attrs={"property": "og:description"})
        if tag and tag.get("content"):
            return tag["content"].replace("\n", " ").strip()

        return None

    def get_difficulty(self) -> Optional[str]:
        """
        Возвращает уровень сложности курса.
        """
        if self.soup is None:
            raise RuntimeError("Soup not prepared. Call parse() first.")

        block = self.soup.find(
            "div",
            attrs={"class": "course-promo__head-widget", "data-type": "difficulty"}
        )

        if not block:
            return None

        text = block.get_text(strip=True)
        return text or None

    def get_certificate_available(self) -> bool:
        """
        Проверяет, есть ли у курса сертификат.
        Возвращает True, если блок сертификата присутствует, иначе False.
        """
        if self.soup is None:
            raise RuntimeError("Soup not prepared. Call parse() first.")

        block = self.soup.find(
            "div",
            attrs={"class": "course-promo__head-widget", "data-type": "certificate"}
        )

        return block is not None

    def get_students_count(self) -> Optional[int]:
        """
        Возвращает количество учащихся на курсе.
        """
        if self.soup is None:
            raise RuntimeError("Soup not prepared. Call parse() first.")

        block = self.soup.find("div", class_="course-promo-summary__students")
        if not block:
            return None

        text = block.get_text(strip=True)
        # Убираем пробелы и слова
        text = (text.replace("\xa0", "").
                replace("учащихся", "").
                replace("учащийся", "").strip())

        try:
            return int(text)
        except ValueError:
            return None

    def get_price(self) -> Optional[int]:
        """
        Возвращает цену курса в рублях.
        Например: '2 490 ₽' -> 2490, '14 900 ₽' -> 14900, '500 ₽' -> 500.
        """
        if self.soup is None:
            raise RuntimeError("Soup not prepared. Call parse() first.")

        container = self.soup.find("div", class_="course-promo-enrollment__price-container")
        if not container:
            return None

        price_span = container.find("span", class_="display-price__price")
        if not price_span:
            return None

        numbers = price_span.find_all("span", attrs={"data-type": "integer"})
        if not numbers:
            return None

        price_str = "".join(span.get("data-value", "") for span in numbers)

        try:
            return int(price_str)
        except ValueError:
            return None

    def get_rating_and_reviews(self) -> tuple[Optional[float], Optional[int]]:
        """
        Возвращает рейтинг курса и количество оценок из скрипта ld+json.
        Например: 4.9, 1035
        """
        if self.soup is None:
            raise RuntimeError("Soup not prepared. Call parse() first.")

        script_tag = self.soup.find("script", type="application/ld+json")
        if not script_tag:
            return None, None

        try:
            data = json.loads(script_tag.string)
            aggregate = data.get("aggregateRating", {})
            rating = round(float(aggregate.get("ratingValue")), 1) if "ratingValue" in aggregate else None
            reviews = int(aggregate.get("ratingCount")) if "ratingCount" in aggregate else None
            return rating, reviews
        except (json.JSONDecodeError, ValueError, TypeError):
            return None, None

    def get_page(self):
        """
        Получает все поля курса и возвращает кортеж:
        title, description, difficulty, certificate_available, students_count, price, rating, reviews_count
        """
        title = self.get_title()
        description = self.get_description()
        difficulty = self.get_difficulty()
        certificate_available = self.get_certificate_available()
        students_count = self.get_students_count()
        price = self.get_price()
        rating, reviews_count = self.get_rating_and_reviews()
        # print(title, description)
        return self.index, title, description, difficulty, certificate_available, students_count, price, rating, reviews_count

    def get_page_retry(self, retries: int = 3) -> dict:
        """
        Возвращает словарь с полями курса.
        Если какое-то поле None, заново делает fetch() и parse(), повторяет получение.
        При этом сохраняет уже полученные корректные значения.
        """
        fields = ["index", "title", "description", "difficulty", "certificate_available",
                  "students_count", "price", "rating", "reviews_count"]

        data = dict.fromkeys(fields, None)

        for attempt in range(retries + 1):
            self.fetch_requests()
            self.parse()
            result = self.get_page()
            current_data = dict(zip(fields, result))

            for key in fields:
                if data[key] is None and current_data[key] is not None:
                    data[key] = current_data[key]

            if None not in data.values():
                return data

            time.sleep(0.2 * (attempt ** 2))
        else:
            try:
                self.fetch_selenium()
                self.parse()
                result = self.get_page()
                current_data = dict(zip(fields, result))

                for key in fields:
                    if data[key] is None and current_data[key] is not None:
                        data[key] = current_data[key]
            except Exception as e:
                print(f"Selenium fetch failed: {e}")

        return data

    def get_result(self) -> dict:
        """
        Возвращает готовый словарь с данными курса после всех необходимых запросов.
        """
        return self.get_page_retry()


if __name__ == "__main__":
    indexec = [216041, 172356, 125685, 187922, 154096, 124803, 5482]
    index = 172356
    index_2 = 5482
    for indexe in indexec:
        parser = StepikCourseParser(indexe)
        pprint(parser.get_result())
