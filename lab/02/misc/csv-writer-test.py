import csv

rows = [
    {'name': 'henry', 'age': '12'},
    {'name': 'john', 'age': '14'},
    {'name': 'jack', 'age': '10'},
    {'name': 'joe', 'age': '13'},
    {'name': 'kev"in', 'age': '11'},
]

with open('test.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, dialect='excel', fieldnames=rows[0].keys())
    writer.writeheader()
    for entry in rows:
        writer.writerow(entry)
