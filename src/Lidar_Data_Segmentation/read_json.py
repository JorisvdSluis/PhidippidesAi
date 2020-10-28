import json


def read_json():
    with open('../Lidar_Parser/output.json') as f:
        data = json.load(f)
    return data
