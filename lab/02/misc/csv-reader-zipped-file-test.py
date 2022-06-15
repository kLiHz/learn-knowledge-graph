import zipfile
from io import TextIOWrapper
import csv

# https://stackoverflow.com/questions/26942476/reading-csv-zipped-files-in-python
# https://stackoverflow.com/questions/50259792/reading-csv-files-from-zip-archive-with-python-3-x

zippedFileName = 'C:/Users/Henry/Downloads/ownthink_v2.zip'
pwd = 'https://www.ownthink.com/'

with zipfile.ZipFile(zippedFileName) as archive:
    with archive.open('ownthink_v2.csv', pwd=bytes(pwd, encoding='utf-8')) as f:
        with TextIOWrapper(f, 'utf-8') as wrappedF:
            reader = csv.reader(wrappedF)
            linesToRead = 10
            while linesToRead > 0:
                try:
                    row = reader.__next__()
                    print(row)
                except StopIteration:
                    break
                except:
                    print(f'Error at line: {reader.line_num}')
                finally:
                    linesToRead -= 1
