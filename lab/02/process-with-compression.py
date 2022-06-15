from myutils import try_resume, dict_write, save_progress
from configurations import inFilename, entitiesFileName, relationsFileName, entitiesFieldNames, relationsFieldNames
import csv
import time
from io import TextIOWrapper
import zipfile

timestr = time.strftime("%Y%m%d-%H%M%S")

entitySet, lineProcessedCount = try_resume()

outEntitiesFileName = entitiesFileName.format(timestr)
outEntitiesZippedFile = zipfile.ZipFile(outEntitiesFileName + '.zip', mode='w', compression=zipfile.ZIP_LZMA)
outEntitiesFile = outEntitiesZippedFile.open(outEntitiesFileName, mode='w')
outEntitiesFileWrapper = TextIOWrapper(outEntitiesFile, newline='', encoding='utf-8')

outRelationsFileName = relationsFileName.format(timestr)
outRelationsZippedFile = zipfile.ZipFile(outRelationsFileName + '.zip', mode='w', compression=zipfile.ZIP_LZMA)
outRelationsFile = outRelationsZippedFile.open(outEntitiesFileName, mode='w')
outRelationsFileWrapper = TextIOWrapper(outRelationsFile, newline='', encoding='utf-8')

entitiesWriter = csv.DictWriter(outEntitiesFileWrapper, dialect='excel', fieldnames=entitiesFieldNames)
relationsWriter = csv.DictWriter(outRelationsFileWrapper, dialect='excel', fieldnames=relationsFieldNames)

with open(inFilename, 'r', newline='') as f:
    print('Start processing.')
    reader = csv.DictReader(f, dialect='excel')
    lineProcessedCountNew = dict_write(reader, entitiesWriter, relationsWriter, entitySet, lineProcessedCount)

if lineProcessedCountNew > lineProcessedCount:
    save_progress(lineProcessedCountNew, entitySet)

print('Closing output files...')
outEntitiesFileWrapper.close()
outEntitiesFile.close()
outEntitiesZippedFile.close()

outRelationsFileWrapper.close()
outRelationsFile.close()
outRelationsZippedFile.close()
