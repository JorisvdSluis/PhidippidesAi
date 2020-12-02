import json


def read_json():
    with open('log/log.json') as f:
        data = json.load(f)
    return data
