import requests
from flask import Flask
from flask import render_template

app = Flask(__name__)


CITIES = [
    'Москва',
    'Владивосток',
    'Санкт-Петербург',
    'Нижний Новогород',
    'Великий Новогород',
]
GEOCODER_API_SERVER = "http://geocode-maps.yandex.ru/1.x/"
MAPS_API_SERVER = "http://static-maps.yandex.ru/1.x/"
APIKEY = "40d1649f-0493-4b70-98ba-98533de7710b"


def get_spn(json_response):
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    lower_crd = list(map(float, toponym['boundedBy']['Envelope']['lowerCorner'].split()))
    upper_crd = list(map(float, toponym['boundedBy']['Envelope']['upperCorner'].split()))
    a, b = upper_crd[0] - lower_crd[0], lower_crd[1] - upper_crd[1]
    return str(max(abs(a * 0.25), abs(a * 0.25)))


@app.route('/')
def index():
    return render_template('index.html',
                           images_path=list(map(lambda s: 'img/' + s + '.png', CITIES)),
                           count=len(CITIES))


if __name__ == '__main__':
    for city in CITIES:
        geocoder_params = {
            "apikey": APIKEY,
            "geocode": city,
            "format": "json"
        }

        response = requests.get(GEOCODER_API_SERVER, params=geocoder_params)
        print(response)
        if response:
            json_response = response.json()

            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            cords = ','.join(toponym["Point"]["pos"].split())
            delta = get_spn(json_response)

            map_params = {
                "ll": cords,
                "spn": ",".join([delta, delta]),
                "l": "sat",
            }

            response = requests.get(MAPS_API_SERVER, params=map_params)
            if not response:
                continue

            map_file = f"static/img/{city}.png"
            with open(map_file, "wb") as file:
                print(cords)
                file.write(response.content)
    app.run(port=8080, host='127.0.0.1')