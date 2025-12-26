from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import time

def get_course_ids(url):
    # Настройка Selenium
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    service = Service()  # путь к chromedriver, если он не в PATH

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    # Ждём подгрузки контента
    time.sleep(3)

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    course_ids = []
    for a in soup.find_all("a", class_="course-card__title"):
        href = a.get("href")
        match = re.search(r'/course/(\d+)', href)
        if match:
            course_ids.append(match.group(1))

    return course_ids

# Пример использования
url = 'https://stepik.org/catalog/167?page=6'
course_ids = get_course_ids(url)
print(course_ids)
print(len(course_ids))
