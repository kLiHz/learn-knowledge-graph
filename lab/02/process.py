from SIGINT_handle import GracefulInterruptHandler
import csv
import time
import os.path

inFilename = 'D:/temp/ownthink_v2/ownthink_v2.csv'

entitiesFileName = './entities-{}.csv'
porpertiesAsValue = ['描述']
entitiesFieldNames = ['name:ID(nId)'] + porpertiesAsValue

relationsFileName = './relations-{}.csv'
relationsFieldNames = [':START_ID(nId)', ':END_ID(eId)', ':TYPE']

entitySetFileName = './entitySet.csv'
entitySetFieldNames = [':ID(eId)', 'name', ':LABEL']

lastProcessingPosFileName = './reader-last-pos.txt'
lineProcessedCount = 0

class EntitySet:
    
    def __init__(self):
        self.cnt = 0
        self.id_of = dict()
        self.label_of_id = dict()
    
    def load_from_file(self, f):
        csvReader = csv.DictReader(f, dialect='excel')
        self.cnt = 0
        for row in csvReader:
            self.id_of[row['name']] = row[':ID(eId)']
            self.label_of_id[row[':ID(eId)']] = row[':LABEL']
            self.cnt += 1

    def get(self, name):
        if name in self.id_of:
            return self.id_of[name]
        else:
            self.cnt += 1
            self.id_of[name] = self.cnt
            self.label_of_id[self.cnt] = 'Entity'
            return self.cnt
    
    def add_label_for_id(self, entityID, label):
        self.label_of_id[entityID] = \
            ';'.join(
                set(self.label_of_id[entityID].split(';') + label)
            )
    
    def dump_to_file(self, f):
        csvWriter = csv.DictWriter(f, dialect='excel', fieldnames=entitySetFieldNames)
        csvWriter.writeheader()
        for name in self.id_of.keys():
            eid = self.id_of[name]
            csvWriter.writerow({
                ':ID(eId)': eid,
                'name': name,
                ':LABEL': self.label_of_id[eid],
            })


entitySet = EntitySet()

if os.path.exists(lastProcessingPosFileName):
    with open(lastProcessingPosFileName, 'r') as f:
        contents = f.read()
    lineProcessedCount = int(contents)
    with open(entitySetFileName, 'r', newline='') as f:
        entitySet.load_from_file(f)
else:
    lineProcessedCount = 0
    with open(lastProcessingPosFileName, 'w') as f:
        f.write(str(lineProcessedCount))

timestr = time.strftime("%Y%m%d-%H%M%S")


labelMapper = {
    '标签': 'Tag',
    '文名': 'Name',
    '别名': 'Name',
    '又称': 'Name',
    '地区': 'Reigon',
    '作品': 'Work',
    '职业': 'Job',
}

with GracefulInterruptHandler() as h:

    outEntitiesFile = open(entitiesFileName.format(timestr), 'w', newline='', encoding='utf-8')
    outRelationsFile = open(relationsFileName.format(timestr), 'w', newline='', encoding='utf-8')

    entitiesWriter = csv.DictWriter(outEntitiesFile, dialect='excel', fieldnames=entitiesFieldNames)
    entitiesWriter.writeheader()

    relationsWriter = csv.DictWriter(outRelationsFile, dialect='excel', fieldnames=relationsFieldNames)
    relationsWriter.writeheader()

    with open(inFilename, 'r', newline='') as f:
        print('Start processing.')

        reader = csv.DictReader(f, dialect='excel')
        
        lastReadn = { 'name:ID(nId)': None }
        
        skipLines = lineProcessedCount
        while skipLines > 0:
            try:
                t = reader.__next__()
                
                if lastReadn['name:ID(nId)'] != t['实体']:
                    del lastReadn
                    lastReadn = dict()
                    lastReadn['name:ID(nId)'] = t['实体']
                
                if t['属性'] in porpertiesAsValue:
                    lastReadn[t['属性']] = t['值']
                else:
                    pass
            except:
                print(f'Error at line: {reader.line_num}')
            finally:
                skipLines -= 1
        
        while True:
            try:
                tuple = reader.__next__()

                entityName = tuple['实体']
                porpertyName = tuple['属性']
                value = tuple['值']

                if porpertyName == '' or value == '':
                    continue

                if entityName != lastReadn['name:ID(nId)']:
                    entitiesWriter.writerow(lastReadn)
                    del lastReadn
                    lastReadn = dict()
                    lastReadn['name:ID(nId)'] = entityName

                if porpertyName in porpertiesAsValue:
                    lastReadn[porpertyName] = value
                else:
                    eid = entitySet.get(value)
                    
                    # Add Label for value Entities
                    l = [ labelMapper[keyword] for keyword in labelMapper.keys() if keyword in porpertyName ]
                    entitySet.add_label_for_id(eid, l)

                    relationsWriter.writerow({
                        ':START_ID(nId)': entityName,
                        ':END_ID(eId)': eid,
                        ':TYPE': porpertyName,
                    })
            except StopIteration:
                entitiesWriter.writerow(lastReadn)
                break
            except:
                print(f'Error at line: {reader.line_num}')
            finally:
                lineProcessedCount += 1

                if lineProcessedCount % 100000 == 0:
                    print(f'Processed {lineProcessedCount} lines.')

                if h.interrupted:
                    print('Keyboard Interrupt')
                    print(f'Processed {lineProcessedCount} lines.')
                    break
        
        print('Saving lines count...')
        with open(lastProcessingPosFileName, 'w') as f:
            f.write(str(lineProcessedCount))
        
        print('Saving entity set...')
        with open(entitySetFileName, 'w', newline='') as f:
            entitySet.dump_to_file(f)

        print('Closing output files...')
        outEntitiesFile.close()
        outRelationsFile.close()

