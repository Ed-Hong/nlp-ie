import sys
import spacy
import nltk
import opennre
from nltk.corpus import wordnet
from util import processArgs, test
from node import Node, Edge

def testOpenNRE():
    model = opennre.get_model('wiki80_cnn_softmax')
    sentence = 'He was the son of Máel Dúin mac Máele Fithrich, and grandson of the high king Áed Uaridnach (died 612).'

    print(sentence.find('Máel Dúin mac Máele Fithrich'))
    print(model.infer({'text': sentence, 'h': {'pos': (18, 46)}, 't': {'pos': (78, 91)}}))

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

def bron_kerbosch():
    A = Node('A')
    B = Node('B')
    C = Node('C')
    D = Node('D')
    E = Node('E')
    F = Node('F')

    A.neighbors = [B, C, E]
    A.weightedEdges = [Edge(A, B, 1), Edge(A, C, 0.5), Edge(A, E, 0.5)]

    B.neighbors = [A, C, D, F]
    B.weightedEdges = [Edge(B, A, 0.5), Edge(B, C, 0.5), Edge(B, D, 0.5), Edge(B, F, 0.5)]
    
    C.neighbors = [A, B, D, F]
    C.weightedEdges = [Edge(C, A, 0.5), Edge(C, C, 0.5), Edge(C, D, 0.5), Edge(C, F, 0.5)]

    D.neighbors = [C, B, E, F]
    D.weightedEdges = [Edge(D, C, 0.5), Edge(D, B, 0.5), Edge(D, E, 0.5), Edge(D, F, 0.5)]

    E.neighbors = [A, D]
    E.weightedEdges = [Edge(E, A, 0.5), Edge(E, D, 0.5)]

    F.neighbors = [B, C, D]
    F.weightedEdges = [Edge(F, B, 0.5), Edge(F, C, 0.5), Edge(F, D, 0.5)]

    all_nodes = [A, B, C, D, E, F]

    def find_cliques(potential_clique=[], remaining_nodes=[], skip_nodes=[], depth=0):
        if len(remaining_nodes) == 0 and len(skip_nodes) == 0:
            print('This is a clique: ', potential_clique)
            print('clique weight: ', clique_weight(potential_clique))
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

    def clique_weight(clique=[]):
        product = 1
        edges = 0

        for node in clique:
            for edge in node.weightedEdges:
                product = product * edge.weight
                edges = edges + 1

        return pow(product, (1 / edges))
                

    total_cliques = find_cliques(remaining_nodes=all_nodes)
    print('Total cliques found:', total_cliques)

def main(argv):
    
    # testSpacy()

    # test()
    # printParseTree(doc)

    # print("TESTING NLTK")
    # nltk.download('wordnet') # Installs WordNet to /Users/{user}/nltk_data

    # testWordNet()

    # print("TESTING OPENNRE")
    # testOpenNRE()

    bron_kerbosch()
    




if __name__ == '__main__':
    main(sys.argv[1:])