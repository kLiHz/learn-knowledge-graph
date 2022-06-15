from io import TextIOWrapper
from typing import Tuple
from SIGINT_handle import GracefulInterruptHandler
from configurations import *
import os.path
import csv

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


def try_resume() -> Tuple[EntitySet, int]:
    entitySet = EntitySet()
    lineProcessedCount = 0
    if os.path.exists(lastProcessingPosFileName):
        # If such file exists, read last count from it.
        print('Record file found. Try recovering from previous progress.')
        with open(lastProcessingPosFileName, 'r') as f:
            contents = f.read()
        lineProcessedCount = int(contents)
        # Assume corresponding entitySet file presents, and load it.
        print('Loading from previous progress...')
        with open(entitySetFileName, 'r', newline='') as f:
            entitySet.load_from_file(f)
        print('Loading complete.')
    else:
        with open(lastProcessingPosFileName, 'w') as f:
            f.write(str(lineProcessedCount))
    return entitySet, lineProcessedCount


def dict_write(reader:csv.DictReader, entitiesWriter:csv.DictWriter, relationsWriter:csv.DictWriter, entitySet:EntitySet, lineProcessedCount:int):
    with GracefulInterruptHandler() as h:
        entitiesWriter.writeheader()
        relationsWriter.writeheader()

        lastReadn = { ':ID(nId)': 0, 'name': 'OwnThink', '描述': 'http://www.ownthink.com/' }
        
        print('Skipping processed lines...')
        skipLines = lineProcessedCount
        while skipLines > 0:
            try:
                t = reader.__next__()
            except:
                print(f'Error at line: {reader.line_num}')
                continue
            finally:
                skipLines -= 1
            
            entityName = t['实体']
            porpertyName = t['属性']
            value = t['值']

            if value == '' or entityName == '' or porpertyName == '':
                continue

            if lastReadn['name'] != entityName:
                lastReadn = {
                    ':ID(nId)': lastReadn[':ID(nId)'] + 1,
                    'name': entityName,
                }
            
            if porpertyName in porpertiesAsValue:
                lastReadn[porpertyName] = value
            
            if h.interrupted:
                break
        
        if h.interrupted: return lineProcessedCount
        else:
            print('Skipping completed.')

        while True:
            try:
                tuple = reader.__next__()
            except StopIteration:
                entitiesWriter.writerow(lastReadn)
                break
            except:
                print(f'Error at line: {reader.line_num}')
                continue
            finally:
                lineProcessedCount += 1

            entityName = tuple['实体']
            porpertyName = tuple['属性']
            value = tuple['值']

            if porpertyName == '' or value == '' or entityName == '':
                continue

            if entityName != lastReadn['name']:
                entitiesWriter.writerow(lastReadn)
                lastReadn = {
                    ':ID(nId)': lastReadn[':ID(nId)'] + 1,
                    'name': entityName,
                }

            if porpertyName in porpertiesAsValue:
                lastReadn[porpertyName] = value
            else:
                eid = entitySet.get(value)
                
                # Add Label for value Entities
                l = [ labelMapper[keyword] for keyword in labelMapper.keys() if keyword in porpertyName ]
                entitySet.add_label_for_id(eid, l)

                relationsWriter.writerow({
                    ':START_ID(nId)': lastReadn[':ID(nId)'],
                    ':END_ID(eId)': eid,
                    ':TYPE': 'Attrib',
                    'AttribName': porpertyName,
                })

            if lineProcessedCount % 100000 == 0:
                print(f'Processed {lineProcessedCount} lines.')

            if h.interrupted:
                print('Keyboard Interrupt')
                print(f'Processed {lineProcessedCount} lines.')
                break
        
        return lineProcessedCount


def save_progress(lineProcessedCount, entitySet):
    print('Saving lines count...')
    with open(lastProcessingPosFileName, 'w') as f:
        f.write(str(lineProcessedCount))

    print('Saving entity set...')
    with open(entitySetFileName, 'w', newline='') as f:
        entitySet.dump_to_file(f)
