import zipfile
from io import TextIOWrapper
import csv

rows = [
    {'name': 'henry', 'age': '12'},
    {'name': 'john', 'age': '14'},
    {'name': '杰克', 'age': '10'},
    {'name': 'joe', 'age': '13'},
    {'name': 'kevin', 'age': '11'},
]

with zipfile.ZipFile('test.csv.zip', mode='w', compression=zipfile.ZIP_LZMA) as archive:
    with archive.open('test.csv', mode='w') as f:
        with TextIOWrapper(f, newline='', encoding='utf-8') as wrappedF:
            writer = csv.DictWriter(wrappedF, dialect='excel', fieldnames=rows[0].keys())
            writer.writeheader()
            for i in range(100000):
                for entry in rows:
                    writer.writerow(entry)
