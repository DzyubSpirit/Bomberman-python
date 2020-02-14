import json
import requests

SERVER_URL = "http://localhost:8080"

GET_PLAYERS_URL = SERVER_URL + "/get-players"
POP_QUEUE_URL = SERVER_URL + "/pop-player"


class Bot:
    def __init__(self, id, username, code):
        self.id = id
        self.username = username
        self.code = code


def fromJSONArray(arr):
    return [Bot(d['user_id'], d['username'], d['code']) for d in arr]


def getN(n):
    bots = []
    for i in range(n):
        resp = requests.get(POP_QUEUE_URL)
        if not resp:
            print("Error getting bots: ", resp.status_code, ": ", resp.content)
            continue

        bots.append(json.loads(resp.content))

    return fromJSONArray(bots)
