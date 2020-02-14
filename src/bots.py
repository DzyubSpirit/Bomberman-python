import json
import requests

SERVER_URL = "http://localhost:8080"

GET_PLAYERS_URL = SERVER_URL + "/get-players"


class Bot:
    def __init__(self, id, name, code):
        self.id = id
        self.name = name
        self.code = code


def fromJSONArray(arr):
    return [Bot(d['id'], d['name'], d['code']) for d in arr]


def get():
    resp = requests.get(GET_PLAYERS_URL)
    if not resp:
        print("Error getting bots: ", resp.status_code, ": ", resp)
        return []

    return fromJSONArray(json.loads(resp.content))
