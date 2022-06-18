inFilename = 'D:/temp/ownthink_v2/ownthink_v2.csv'

entitiesFileName = './entities-{}.csv'
propertiesAsValue = ['描述']
entitiesFieldNames = [':ID(nId)', 'name'] + propertiesAsValue

relationsFileName = './relations-{}.csv'
relationsFieldNames = [':START_ID(nId)', ':END_ID(eId)', ':TYPE', 'AttribName']

entitySetFileName = './entitySet.csv'
entitySetFieldNames = [':ID(eId)', 'name', ':LABEL']

lastProcessingPosFileName = './reader-last-pos.txt'

labelMapper = {
    '标签': 'Tag',
    '文名': 'Name',
    '别名': 'Name',
    '又称': 'Name',
    '地区': 'Reigon',
    '作品': 'Work',
    '职业': 'Job',
}
