import os
import sys
import spacy
import nltk
import opennre

from nltk.corpus import wordnet
from util import loadFile
from node import Node, Edge
from template import Buy, Work, Part

def testOpenNRE():
    model = opennre.get_model('wiki80_cnn_softmax')
    sentence = 'He was the son of Máel Dúin mac Máele Fithrich, and grandson of the high king Áed Uaridnach (died 612).'

    print(sentence.find('Máel Dúin mac Máele Fithrich'))
    print(model.infer({'text': sentence, 'h': {'pos': (18, 46)}, 't': {'pos': (78, 91)}}))

def nre(text, head, tail):
    model = opennre.get_model('wiki80_bert_softmax')

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

def testWordNet():
    syn = list()
    ant = list()

    for synset in wordnet.synsets("Worse"):
        for lemma in synset.lemmas():
            syn.append(lemma.name())    #add the synonyms
            if lemma.antonyms():    #When antonyms are available, add them into the list
                ant.append(lemma.antonyms()[0].name())

    print('Synonyms: ' + str(syn))
    print('Antonyms: ' + str(ant))

    print('Hypernyms of car: ')
    print(wordnet.synset('car.n.01').hypernyms())

    print('Hyponyms of car: ')
    print(wordnet.synset('car.n.01').hyponyms())

    print('Meronyms of car: ')
    print(wordnet.synset('car.n.01').member_holonyms())
    print(wordnet.synset('car.n.01').part_meronyms())
    print(wordnet.synset('car.n.01').substance_meronyms())

    print('Holonyms: ')
    print(wordnet.synset('atom.n.01').part_holonyms())
    print(wordnet.synset('hydrogen.n.01').substance_holonyms())
    print(wordnet.synset('cat.n.01').member_holonyms())

def testSpacy():
    # Load English tokenizer, tagger, parser, NER and word vectors
    nlp = spacy.load("en_core_web_sm")

    # Process whole documents
    text = ("When Sebastian Thrun started working on self-driving cars at "
            "Google in 2007, few people outside of the company took him "
            "seriously. “I can tell you very senior CEOs of major American "
            "car companies would shake my hand and turn away because I wasn’t "
            "worth talking to,” said Thrun, in an interview with Recode earlier "
            "this week.")
    doc = nlp(text)

    print("Sentences:", [sent.text for sent in doc.sents])
    print("Tokens:", [token.text for token in doc])
    print("Lemmas:", [token.lemma_ for token in doc])
    print("POS:", [token.pos_ for token in doc])
    print("Tags:", [token.tag_ for token in doc])

    print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
    print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])
    print("Named Entities:", [ent.text for ent in doc.ents])

    # Find named entities, phrases and concepts
    for entity in doc.ents:
        print(entity.text, entity.label_)

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

            if cliqueWeight > 0.50:
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

# testSpacy()
# printParseTree(doc)

# print("TESTING NLTK")
# nltk.download('wordnet') # Installs WordNet to /Users/{user}/nltk_data
# testWordNet()
def main(argv):
    if len(sys.argv) < 2:
        print("pass filename")
        sys.exit(2)
    print("loading " + argv[0])

    # texts = loadFile(argv[0])
    texts = ['Rami Eid is studying at Stony Brook University in New York']

    nlp = spacy.load("en_core_web_sm")
    for idx, doc in enumerate(nlp.pipe(texts, disable=["tagger", "parser"])):
        # Do something with the doc here
        #print("Tokens:", [token.text for token in doc])
        print("Named Entities:", [(ent.text, ent.label_) for ent in doc.ents])
        print()

        # build graph nodes: <key, value> = <Entity name, Node>
        nodes = {}
        for ent in doc.ents:
            n = Node(ent)
            nodes[ent.text] = n

        for ent1 in doc.ents:
            n = nodes[ent1.text]

            for ent2 in doc.ents:
                if ent1 != ent2:
                    print(ent1, ent2, sep=" *** ")
                    relation = nre(texts[idx], ent1.text, ent2.text)
                    print()

                    # build graph
                    n.neighbors.append(nodes[ent2.text])
                    n.addWeightedEdge(nodes[ent2.text], relation[0], relation[1])

        # verifying graph
        print("Graph: ")
        for key, val in nodes.items():
            print('Node:', key)
            for neighbor in val.neighbors:
                print('Neighbor:', neighbor)
            for edge in val.weightedEdges:
                print('Edge:', edge.src, edge.dst, edge.relation, edge.weight)

        print("BRON-KERBOSCH")
        # Find maximal cliques and clique weights
        cliques = bron_kerbosch(list(nodes.values()))
        print("cliques:",cliques)

        # if the clique contains certain types of relations, then we fill them into the complex relation / template
        workTemplates = []
        for clique in cliques:
            for node in clique:
                for edge in node.weightedEdges:
                    if edge.dst in clique:
                        if edge.relation == 'work location':
                            # make new WORK template
                            work = Work()

                            # fill in the PERSON field of the WORK template
                            if edge.src.entity.label_ == 'PERSON':
                                work.person = edge.src.name

                            # other fields...

                            workTemplates.append(work)


                        # if edge.relation == 'headquarters location':
                            # make new PART template

        # verifying template filling
        for work in workTemplates:
            print('Work:', work.person, work.org, work.title, work.location)

if __name__ == '__main__':
    main(sys.argv[1:])