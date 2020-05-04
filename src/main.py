import sys, json
import jsons
import os
import spacy
import nltk
import opennre
import torch

from opennre import encoder, model, framework
from nltk.corpus import wordnet
from util import loadFile
from node import Node, Edge
from template import Buy, Work, Part, Output, Extraction

def getModel():
    rel2id = json.load(open('../data/dataset/wiki80/wiki80_rel2id.json'))
    sentence_encoder = encoder.BERTEncoder(max_length=88, pretrain_path='../data/pretrain/bert-base-uncased')
    m = model.SoftmaxNN(sentence_encoder, len(rel2id), rel2id)
    m.load_state_dict(torch.load('ckpt/wiki80_bert_softmax.pth.tar', map_location='cpu')['state_dict'])
    return m

def nre(text, head, tail):
    model = opennre.get_model('wiki80_bert_softmax')
    #model = getModel()

    hStart = text.find(head)
    hEnd = hStart + len(head)

    tStart = text.find(tail)
    tEnd = tStart + len(tail)

    relation = model.infer({'text': text, 'h': {'pos': (hStart, hEnd)}, 't': {'pos': (tStart, tEnd)}})
    print(relation)
    return relation

def printParseTree(doc):
    for token in doc:
        print(token.text, token.dep_, token.head.text, token.head.pos_,
            [child for child in token.children])

def wordNet(word):
    # nltk.download('wordnet') # Installs WordNet to /Users/{user}/nltk_data

    for synset in wordnet.synsets(word):
        print('Hypernyms of',word)
        print(synset.hypernyms())

        print('Hyponyms of',word)
        print(synset.hyponyms())

        print('Meronyms of',word)
        print(synset.part_meronyms())
        print(synset.substance_meronyms())

        print('Holonyms of',word)
        print(synset.part_holonyms())
        print(synset.substance_holonyms())


def task1(text):
    # Load English tokenizer, tagger, parser, NER and word vectors
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    print("Sentences:", [sent.text for sent in doc.sents])
    print("Tokens:", [token.text for token in doc])
    print("Lemmas:", [token.lemma_ for token in doc])
    print("POS:", [token.pos_ for token in doc])
    print("Tags:", [token.tag_ for token in doc])
    print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
    print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])
    print("Named Entities:", [ent.text for ent in doc.ents])

    # Named entities and their type
    for entity in doc.ents:
        print(entity.text, entity.label_)

    # Using wordNet to extract Hypernyms, Hyponyms, etc
    for token in doc:
        wordNet(token.text)

    # Parse Tree
    printParseTree(doc)

def bron_kerbosch(nodesList):
    cliques = []

    def clique_weight(clique=[]):
        product = 1
        edges = 0

        for node in clique:
            for edge in node.weightedEdges:
                product = product * edge.weight
                edges = edges + 1

        return pow(product, (1 / edges))

    def find_cliques(potential_clique=[], remaining_nodes=[], skip_nodes=[], depth=0):
        if len(remaining_nodes) == 0 and len(skip_nodes) == 0:
            print('This is a clique: ', potential_clique)

            cliqueWeight = clique_weight(potential_clique)
            print('clique weight: ', cliqueWeight)

            if cliqueWeight > 0.40:
                cliques.append(potential_clique)

            return 1

        found_cliques = 0
        for node in remaining_nodes:
            # Try adding the node to the current potential_clique to see if we can make it work.
            new_potential_clique = potential_clique + [node]
            new_remaining_nodes = [n for n in remaining_nodes if n in node.neighbors]
            new_skip_list = [n for n in skip_nodes if n in node.neighbors]
            found_cliques += find_cliques(new_potential_clique, new_remaining_nodes, new_skip_list, depth + 1)

            # We're done considering this node.  If there was a way to form a clique with it, we
            # already discovered its maximal clique in the recursive call above.  So, go ahead
            # and remove it from the list of remaining nodes and add it to the skip list.
            remaining_nodes.remove(node)
            skip_nodes.append(node)

        return found_cliques

    total_cliques = find_cliques(remaining_nodes=nodesList)
    print('Total cliques found:', total_cliques)
    return cliques

def buildEntityGraph(doc, text):
    nodes = {}
    for ent in doc.ents:
        n = Node(ent)
        nodes[ent.text] = n

    for ent1 in nodes:
        n = nodes[ent1]
        for ent2 in doc.ents:
            if ent1 != ent2.text:
                print(ent1, ent2, sep=" -> ")
                relation = nre(text, ent1, ent2.text)
                print()

                n.neighbors.append(nodes[ent2.text])
                n.addWeightedEdge(nodes[ent2.text], relation[0], relation[1])
    
    return nodes

def printGraph(nodes):
    for key, val in nodes.items():
        print('Node:', key)
        for neighbor in val.neighbors:
            print('Neighbor:', neighbor)
        for edge in val.weightedEdges:
            print('Edge:', edge.src, edge.dst, edge.relation, edge.weight)

def addIgnoreDuplicate(template, templateList):
    if template not in templateList: 
        templateList.append(template)

def tryAddWorkTemplate(edge, workTemplates):
    template = Work()
    nonNull = False
    if edge.relation == 'work location':
        if edge.src.entity.label_ == 'PERSON':
            template.person = edge.src.name
            nonNull = True
        if edge.dst.entity.label_ == 'ORG':
            template.org = edge.dst.name
            nonNull = True
        if edge.dst.entity.label_ == 'GPE':
            template.location = edge.dst.name
            nonNull = True
        if nonNull:
            addIgnoreDuplicate(template, workTemplates)
    
    if edge.relation in ['field of work', 'position held']:
        if edge.src.entity.label_ == 'PERSON':
            template.person = edge.src.name
            template.title = edge.dst.name
        if nonNull:
            addIgnoreDuplicate(template, workTemplates)

    if edge.relation == 'head of government':
        if edge.src.entity.label_ == 'PERSON':
            template.person = edge.src.name
            template.title = 'head of government'
            nonNull = True
        if edge.dst.entity.label_ == 'ORG':
            template.org = edge.dst.name
            nonNull = True
        if edge.dst.entity.label_ == 'GPE':
            template.location = edge.dst.name
            nonNull = True
        if nonNull:
            addIgnoreDuplicate(template, workTemplates)

    if edge.relation == 'owned by':
        if edge.dst.entity.label_ == 'PERSON':
            template.person = edge.dst.name
            template.title = 'owner'
            nonNull = True
        if edge.src.entity.label_ == 'ORG':
            template.org = edge.src.name
            nonNull = True
        if nonNull:
            addIgnoreDuplicate(template, workTemplates)

    if edge.relation == 'architect':
        if edge.src.entity.label_ == 'PERSON':
            template.person = edge.src.name
            template.title = 'architect'
            nonNull = True
        if nonNull:
            addIgnoreDuplicate(template, workTemplates)
            
    if edge.relation == 'director':
        if edge.src.entity.label_ == 'PERSON':
            template.person = edge.src.name
            template.title = 'director'
            nonNull = True
        if nonNull:
            addIgnoreDuplicate(template, workTemplates)
            
    # inferring that the place of residence is the same as work location
    if edge.relation == 'residence':
        if edge.src.entity.label_ == 'PERSON':
            prevTemplates = [t for t in workTemplates if t.person == edge.src.name and not t.location]
            for prevTemp in prevTemplates:
                prevTemp.location = edge.dst.name

def tryAddPartTemplate(edge, partTemplates):
    template = Part()
    if edge.relation == 'contains administrative territorial entity':
        if edge.src.entity.label_ in ['FAC', 'GPE', 'LOC'] and edge.dst.entity.label_ in ['FAC', 'GPE', 'LOC']:
            template.whole = edge.src.name
            template.part = edge.dst.name
            addIgnoreDuplicate(template, partTemplates)

    if edge.relation == 'has part':
        if edge.src.entity.label_ in ['FAC', 'GPE', 'LOC'] and edge.dst.entity.label_ in ['FAC', 'GPE', 'LOC']:
            template.whole = edge.src.name
            template.part = edge.dst.name
            addIgnoreDuplicate(template, partTemplates)

    if edge.relation == 'located on terrain feature':
        if edge.src.entity.label_ in ['FAC', 'GPE', 'LOC'] and edge.dst.entity.label_ in ['FAC', 'GPE', 'LOC']:
            template.part = edge.src.name
            template.whole = edge.dst.name
            addIgnoreDuplicate(template, partTemplates)

    if edge.relation == 'country':
        if edge.src.entity.label_ in ['FAC', 'GPE', 'LOC'] and edge.dst.entity.label_ in ['FAC', 'GPE', 'LOC']:
            template.part = edge.src.name
            template.whole = edge.dst.name
            addIgnoreDuplicate(template, partTemplates)

    if edge.relation == 'location':
        if edge.src.entity.label_ in ['FAC', 'GPE', 'LOC'] and edge.dst.entity.label_ in ['FAC', 'GPE', 'LOC']:
            template.part = edge.src.name
            template.whole = edge.dst.name
            addIgnoreDuplicate(template, partTemplates)

    if edge.relation == 'located in the administrative territorial entity':
        if edge.src.entity.label_ in ['FAC', 'GPE', 'LOC'] and edge.dst.entity.label_ in ['FAC', 'GPE', 'LOC']:
            template.part = edge.src.name
            template.whole = edge.dst.name
            addIgnoreDuplicate(template, partTemplates)

    if edge.relation == 'part of':
        if edge.src.entity.label_ in ['FAC', 'GPE', 'LOC'] and edge.dst.entity.label_ in ['FAC', 'GPE', 'LOC']:
            template.part = edge.src.name
            template.whole = edge.dst.name
            addIgnoreDuplicate(template, partTemplates)

    if edge.relation == 'located in or next to body of water':
        if edge.src.entity.label_ in ['FAC', 'GPE', 'LOC'] and edge.dst.entity.label_ in ['FAC', 'GPE', 'LOC']:
            template.part = edge.src.name
            template.whole = edge.dst.name
            addIgnoreDuplicate(template, partTemplates)

    if edge.relation == 'member of':
        if edge.src.entity.label_ in ['FAC', 'GPE', 'LOC'] and edge.dst.entity.label_ in ['FAC', 'GPE', 'LOC']:
            template.part = edge.src.name
            template.whole = edge.dst.name
            addIgnoreDuplicate(template, partTemplates)



def main(argv):
    if len(sys.argv) < 2:
        print("pass filename")
        sys.exit(2)
    print("loading " + argv[0])

    texts = loadFile(argv[0])
    # debug
    # texts = ['Rami Eid is studying at Stony Brook University in New York.',
    #          'Blounts Creek is a small unincorporated rural community in Beaufort County, North Carolina, United States, near a creek with the same name.']

    # task 1
    #task1(texts[0])

    nlp = spacy.load("en_core_web_sm")
    for idx, doc in enumerate(nlp.pipe(texts, disable=["tagger", "parser"])):
        print("Named Entities:", [(ent.text, ent.label_) for ent in doc.ents])

        # Represent entity graph as dictionary: <Entity name, Node>
        nodes = buildEntityGraph(doc, texts[idx])

        # verifying graph
        print("Graph:")
        printGraph(nodes)

        # Find maximal cliques and clique weights
        print("BRON-KERBOSCH")
        sys.setrecursionlimit(2000)
        cliques = bron_kerbosch(list(nodes.values()))
        print("cliques:", cliques)

        # if the clique contains certain types of relations, then we fill them into the complex relation / template
        workTemplates = []
        partTemplates = []

        for clique in cliques:
            for node in clique:
                for edge in node.weightedEdges:
                    if edge.dst in clique:
                        tryAddWorkTemplate(edge, workTemplates)
                        tryAddPartTemplate(edge, partTemplates)
                        #tryAddBuyTemplate(edge, partTemplates)

        # verifying template filling
        for work in workTemplates:
            print('Work:', work.person, work.org, work.title, work.location, sep=', ')

        for part in partTemplates:
            print(part.part, part.whole,sep=' part of ')

        # writing templates to json output
        out = []
        for template in workTemplates:
            arguments = {}
            arguments['1'] = template.person or ""
            arguments['2'] = template.org or ""
            arguments['3'] = template.title or ""
            arguments['4'] = template.location or ""
            
            extraction = Extraction('WORK', [token.text for token in doc], arguments)
            output = Output(argv[0], extraction)
            out.append(output)

        for template in partTemplates:
            arguments = {}
            arguments['1'] = template.part or ""
            arguments['2'] = template.whole or ""
            
            extraction = Extraction('PART', [token.text for token in doc], arguments)
            output = Output(argv[0], extraction)
            out.append(output)

        # Write new relations to data file
        jsons.suppress_warnings()
        for output in out:
            with open(str(argv[0])[:-4] + '.json', 'a') as the_file:
                the_file.write(json.dumps(jsons.dump(output)) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:])