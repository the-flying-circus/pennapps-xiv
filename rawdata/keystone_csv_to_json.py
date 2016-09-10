import json
import csv

rd = csv.reader(open('keystone.csv', newline=''))
wr = open('keystone.json', 'w')
data = list()
for row in rd:
    if row[1][len(row[1]) - 2:len(row[1])] == 'SD' and row[4] == '11' and row[5] == 'All Students' and row[7] != 'IS' and row[7] != 'NA':
        data.append(json.dumps({'id': int(row[0]), 'district': row[1], 'school': row[2], 'subject': row[3], 'adv': float(row[7]), 'pro': float(row[8]), 
            'basic': float(row[9]), 'below': float(row[10])}))
json.dump(data, wr)