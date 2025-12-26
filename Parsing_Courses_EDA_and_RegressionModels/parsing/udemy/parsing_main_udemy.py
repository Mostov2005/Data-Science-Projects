import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from parsing_solo_page_udemy import *

# Файл со ссылками
input_file = "udemy_pages.json"

# Файл для сохранения результата
output_file = "udemy_courses_data.csv"

# Загружаем JSON со всеми страницами
with open(input_file, "r", encoding="utf-8") as f:
    all_pages = json.load(f)

# Создаём DataFrame
all_df = pd.DataFrame(columns=[
    "index", "title", "description", "difficulty", "certificate_available",
    "students", "price", "rating", "reviews_count", "source", "course"
])


def process_course(entry):
    """
    Функция для многопоточности.
    entry = (url, difficulty)
    """
    url, diff = entry
    try:
        data = get_result(
            url=url,
            difficulty=diff
        )
        return data
    except Exception as e:
        print(f"Ошибка: {url} — {e}")
        return None


# Собираем список всех курсов вида (url, difficulty)
tasks = []
for page, courses in all_pages.items():
    for course_info in courses:
        full_url = "https://www.udemy.com" + course_info["url"]
        tasks.append((full_url, course_info["complexity"]))

saved = 0

with ThreadPoolExecutor(max_workers=9) as executor:
    futures = [executor.submit(process_course, task) for task in tasks]
    for future in as_completed(futures):
        result = future.result()
        if result is None:
            continue

        # Добавляем в DataFrame
        all_df.loc[len(all_df)] = result
        all_df.to_csv(output_file, index=False, encoding="utf-8")

        saved += 1
        print(f"✔ Сохранено {saved} — {result['index']}")
        time.sleep(0.1)
