import json
from parsing_inxexec_course_stepik_requests import get_course_ids_requests

data_page = {"Python": 208,
             "SQL": 164,
             "Программирование": 166,
             "Анализ данных и DS": 167,
             "Веб-разработка": 165,
             "Инструменты DevOps": 280,
             "C/C++": 311,
             "Java": 310,
             "HTML/CSS": 322,
             "JavaScript": 314,
             "Машинное обучение и наука о данных": 350,
             "Анализ данных": 348}

page_count = {208: 5,
              164: 3,
              166: 9,
              167: 6,
              165: 5,
              280: 3,
              311: 9,
              310: 8,
              322: 6,
              314: 10,
              350: 10,
              348: 10}

all_courses = {}

for key, value in data_page.items():
    url = f'https://stepik.org/catalog/{value}'
    print(url)
    course_ids = get_course_ids_requests(url)
    if len(course_ids) == 0:
        course_ids = get_course_ids_requests(url)
    if len(course_ids) == 0:
        course_ids = get_course_ids_requests(url)
    if len(course_ids) == 0:
        continue  # 3 попытки

    course_ids = list(map(int, course_ids))
    all_courses[key] = course_ids

with open("stepik_courses.json", "w", encoding="utf-8") as f:
    json.dump(all_courses, f, ensure_ascii=False, indent=4)
