import json
import csv

a = 'one'
print(a[len(a)-2:len(a)])

rd = csv.reader(open('keystone.csv', newline=''))
wr = open('keystone.json', 'w')
for row in rd:
    if row[1][len(row[1]) - 2:len(row[1])] == 'SD' and row[4] == '11' and row[5] == 'All Students' and row[7] != 'IS' and row[7] != 'NA':
        print(json.dumps({'id': int(row[0]), 'name': row[1], 'subject': row[3], 'adv': float(row[7]), 'pro': float(row[8]), 
            'basic': float(row[9]), 'below': float(row[10])}), wr)
#json.dump(open('keystone.json', 'w'), fp)