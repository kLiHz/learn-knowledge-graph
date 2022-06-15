from myutils import try_resume, dict_write, save_progress
from configurations import inFilename, entitiesFileName, relationsFileName, entitiesFieldNames, relationsFieldNames
import csv
import time

timestr = time.strftime("%Y%m%d-%H%M%S")

entitySet, lineProcessedCount = try_resume()

outEntitiesFile = open(entitiesFileName.format(timestr), 'w', newline='', encoding='utf-8')
outRelationsFile = open(relationsFileName.format(timestr), 'w', newline='', encoding='utf-8')

entitiesWriter = csv.DictWriter(outEntitiesFile, dialect='excel', fieldnames=entitiesFieldNames)
relationsWriter = csv.DictWriter(outRelationsFile, dialect='excel', fieldnames=relationsFieldNames)

with open(inFilename, 'r', newline='') as f:
    print('Start processing.')
    reader = csv.DictReader(f, dialect='excel')
    lineProcessedCountNew = dict_write(reader, entitiesWriter, relationsWriter, entitySet, lineProcessedCount)

if lineProcessedCountNew > lineProcessedCount:
    save_progress(lineProcessedCountNew, entitySet)

print('Closing output files...')
outEntitiesFile.close()
outRelationsFile.close()
