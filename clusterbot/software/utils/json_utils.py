import json

def read(filename):
    with open(filename) as f:
        return json.load(f)

def write(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f)