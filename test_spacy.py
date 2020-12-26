import spacy
from spacy import displacy
import test_sentences

nlp = spacy.load('en_core_web_sm')

def print_text(text):
    doc = nlp(text)
    for token in doc:
        print (token.text, token.head, token.dep_)
    print()

displacy.serve(nlp(test_sentences.sents[-1]), style='dep')
