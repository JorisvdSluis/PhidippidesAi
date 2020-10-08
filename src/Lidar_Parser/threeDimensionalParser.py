import csv
import numpy as np
import json

with open('../../docs/logs/log.txt', "r") as textFile:
    k = 0
    with open('output.txt', 'w') as f:

        for line in textFile:
            k += 1
            line = line.replace("(", "")
            line = line.replace(",", " ")
            first = str(line).split(" - ")[0]
            f.write(first)
            f.write("\n")

    print(k)
