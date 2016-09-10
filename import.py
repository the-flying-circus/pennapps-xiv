#!/usr/bin/env python3

import sys
import csv
import pymongo
from datetime import datetime
from secret import DB_URL

crime_file = "../crime_philadelphia.csv"
collisions_file = "../collisions_philadelphia.csv"

client = pymongo.MongoClient(DB_URL)
db = client["homie"]

crime = db["crime"]
crime.drop()
crime.create_index([("coord", pymongo.GEO2D)])

with open(crime_file) as f:
    reader = csv.reader(f)
    print(next(reader, None))
    count = 0
    for row in reader:
        if count > 1000000:
            break
        loc = row[-2]
        if not loc.startswith("POINT"):
            continue
        loc = [float(x) for x in loc[7:-1].split(" ")]
        crime.insert_one({
            "coord": loc,
            "type": row[-3],
            "time": datetime.strptime(row[2], "%m/%d/%Y %I:%M:%S %p")
        })
        count += 1

collisions = db["collisions"]
collisions.drop()
collisions.create_index([("coord", pymongo.GEO2D)])

with open(collisions_file) as f:
    reader = csv.reader(f)
    print(next(reader, None))
    for row in reader:
        collisions.insert_one({
            "coord": [float(row[0]), float(row[1])],
            "year": int(row[4]),
            "month": int(row[5])
        })

client.close()
