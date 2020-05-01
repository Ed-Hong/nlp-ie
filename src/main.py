import sys
import spacy
import nltk
from nltk.corpus import wordnet
from util import processArgs, test

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


def main(argv):
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

    test()
    printParseTree(doc)

    print("TESTING NLTK")
    # nltk.download('wordnet') # Installs WordNet to /Users/{user}/nltk_data

    testWordNet()



if __name__ == '__main__':
    main(sys.argv[1:])