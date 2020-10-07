import csv
import numpy as np
import json

with open('../../docs/logs/log.txt', "r") as textFile:
    jsonObject = []
    for line in textFile:
        line = line.replace("(", "")
        line = line.replace(")", "")
        line = line.replace(" - ", ",")
        j = 0
        x = ''
        y = ''
        z = ''
        i = ''
        for word in str(line).split(","):
            if j == 0:
                x = word
            elif j == 1:
                y = word
            elif j == 2:
                z = word
            else:
                i = word.replace("\n", "")
            j += 1
        try:
            jsonObject.append({
                "x": float(x),
                "y": float(y),
                "z": float(z),
                "i": float(i),
            })
        except ValueError:
            break
        j = 0
    with open('output.json', 'w') as f:
        json.dump(jsonObject, f)
