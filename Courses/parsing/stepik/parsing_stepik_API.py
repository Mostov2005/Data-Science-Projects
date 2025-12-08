import requests
from settings import client_id, client_secret
from pprint import pprint

# Получаем токен
auth = requests.post(
    "https://stepik.org/oauth2/token/",
    data={"grant_type": "client_credentials"},
    auth=(client_id, client_secret)
)
token = auth.json()['access_token']

headers = {"Authorization": f"Bearer {token}"}

# Запрос по одному ID
indexec = [118518, 55918, 96832, 197191, 253161, 214865, 124803, 115372, 125685, 185939, 216041, 115517, 125859, 115617,
           116440, 115662, 113402, 187221, 180000, 126012, 118206, 218864, 133183, 133280, 181092, 175966, 197220,
           206133, 247417, 193674, 183142,
           233204, 171974, 207238, 97188, 229484, 179999, 101173, 216279, 174887, 126716, 206901, 113652, 113803,
           115252,
           243521, 184350, 199780, 230295, 215129, 222599, 230302, 113802, 241005, 202590, 204157, 181927,
           97259, 177416, 210038, 232634, 243796, 237148, 254281, 187191, 201589, 233592,
           251069, 250785, 200964, 252235, 233341, 251216, 236047, 251336, 242317,
           213700, 183213, 246596, 251929, 236205, 215410, 233720, 250833, 244991,
           256433, 245200, 256311, 247015, 229575, 245372, 256176, 240525, 258529]
for index in indexec:
    resp = requests.get(f"https://stepik.org/api/courses/{index}", headers=headers)
    course = resp.json()['courses'][0]
    pprint(course)
    print(course['id'], course['title'], course['learners_count'])
