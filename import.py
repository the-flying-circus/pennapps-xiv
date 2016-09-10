#!/usr/bin/env python3

import sys
import csv

crime_file = "../crime_philadelphia.csv"
collisions_file = "../collisions_philadelphia.csv"

with open(crime_file) as f:
    reader = csv.reader(f)
    print(next(reader, None))
    for row in reader:
        pass

with open(collisions_file) as f:
    reader = csv.reader(f)
    print(next(reader, None))
    for row in reader:
        pass
