import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def save_results(filename, data):
    path = os.path.join(BASE_DIR, filename)

    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    return path