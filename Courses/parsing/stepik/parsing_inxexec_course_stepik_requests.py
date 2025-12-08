import requests
from bs4 import BeautifulSoup
import json
import re


def get_course_ids_requests(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка при запросе: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    # print(soup)

    for script in soup.find_all("script"):
        if script.string and '"course-list"' in script.string:
            json_text_match = re.search(r'({.*"course-lists".*})', script.string, re.DOTALL)
            if json_text_match:
                json_text = json_text_match.group(1)
                try:
                    data = json.loads(json_text)
                    # print(data)
                    course_lists = data['records']['course-list']['course-lists']
                    first_list = course_lists[0]
                    course_ids = first_list.get("courses", [])
                    return course_ids
                except:
                    continue

    return []


# url = 'https://stepik.org/catalog/167'
# course_ids = get_course_ids(url)
# print(course_ids)
# print(len(course_ids))  # теперь должно быть 94
