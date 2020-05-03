import sys
import os
import json
import jsons
import spacy
from util import loadFile

maxId = 0

class Relation(object):
    def __init__(self, tokens, head, tail):
        self.token = tokens
        self.h = head
        self.t = tail

    def __repr__(self):
        return self.token, self.h, self.t

class Entity(object):
    def __init__(self, pos, name=None, id=None):
        self.name = name
        self.id = id
        self.pos = pos  # tuple (start, end)

    def __repr__(self):
        return self.name, self.id, self.pos

def getMaxId(ids):
    max = 0
    for name in ids:
        idInt = int(str(ids[name][1:]))
        if idInt > max:
            max = idInt

    return max

def loadDataSet():
    ids = {}
    for entry in os.scandir('./'):
        if entry.path.endswith('.txt') and entry.is_file():
            lines = loadFile(entry.path)
            for line in lines:
                # Parse json
                ex = json.loads(line)

                # add to entity ids
                if ex['h']['name'] not in ids:
                    ids[ex['h']['name']] = ex['h']['id']

                if ex['t']['name'] not in ids:
                    ids[ex['t']['name']] = ex['t']['id']

    return ids

def addRelations(tokens, ids, newRelations):
    while True:
        relation = input('relation? ')
        if relation == 'no':
            break
        
        if relation == 'buyer of':
            addRelation('buyer of', tokens, ids, newRelations)


def addRelation(type, tokens, ids, newRelations):
    global maxId

    hStart = int(input('hStart? '))
    hEnd = int(input('hEnd? '))

    tStart = int(input('tStart? '))
    tEnd = int(input('tEnd? '))

    head = Entity((hStart, hEnd))
    head.name = ' '.join(tokens[hStart:hEnd]).lower().strip()

    if head.name in ids:
        head.id = ids[head.name]
    else:
        head.id = 'Q' + str(maxId + 1)
        maxId = maxId + 1
        ids[head.name] = head.id
    
    tail = Entity((tStart, tEnd))
    tail.name = ' '.join(tokens[tStart:tEnd]).lower().strip()

    if tail.name in ids:
        tail.id = ids[tail.name]
    else:
        tail.id = 'Q' + str(maxId + 1)
        maxId = maxId + 1
        ids[tail.name] = tail.id

    rel = Relation(tokens, head, tail)
    newRelations.append(rel)


def main(argv):
    global maxId

    # Named Entity ids: <Name, id>
    ids = loadDataSet()
    maxId = getMaxId(ids)
    newRelations = []
    nlp = spacy.load("en_core_web_sm")

    for entry in os.scandir('../temp/'):
        if entry.path.endswith('.txt') and entry.is_file():
            lines = loadFile(entry.path)
            for line in lines:
                doc = nlp(line)

                for sentence in doc.sents:
                    for idx,token in enumerate(sentence):
                        print(idx, token, sep=':')
                    
                    print(sentence)
                    tokens = [token.text for token in doc]
                    addRelations(tokens, ids, newRelations)

                    # Write new relations to data file
                    for relation in newRelations:
                        with open('newRelations.txt', 'a') as the_file:
                            the_file.write(json.dumps(jsons.dump(relation)) + '\n')
    
                



if __name__ == '__main__':
    main(sys.argv[1:])