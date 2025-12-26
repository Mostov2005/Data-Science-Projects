import json
import time

import pandas as pd
from parsing_solo_page_stepik import StepikCourseParser

# Загружаем JSON с курсами
with open("stepik_courses_2.json", "r", encoding="utf-8") as f:
    all_courses = json.load(f)

output_file = "stepik_courses_data.csv"

all_df = pd.DataFrame(columns=[
    "index", "title", "description", "difficulty", "certificate_available",
    "students_count", "price", "rating", "reviews_count", "source", "course"
])
count = 0

for course, indexes in all_courses.items():
    for index in indexes:
        try:
            parser = StepikCourseParser(index)
            result = parser.get_result()

            result["source"] = "stepik"
            result["course"] = course

            all_df.loc[len(all_df)] = result
            all_df.to_csv(output_file, index=False, encoding="utf-8")
            count += 1
            print(f"Сохранено: {course} {count}")
            time.sleep(0.2)
        except:
            continue
