__author__ = "Oliver Jiang"

import spacy
from spacy.matcher import Matcher
from spacy.util import filter_spans
import lemminflect
from lemminflect import getLemma, getInflection
nlp = spacy.load('en_core_web_sm')

def extract_verb_slices(sent_doc):
    """
    Slices the verb and its aux/neg children from sent_doc.
    @param sent_doc: a spacy doc, containing a sentence.
    @return: a list of spacy spans, each representing a different verb and its aux/neg children.
    """
    # solution from: https://stackoverflow.com/questions/47856247/extract-verb-phrases-using-spacy
    pattern = [{'POS': 'VERB', 'OP': '?'},
               {'POS': 'ADV', 'OP': '*'},
               {'POS': 'AUX', 'OP': '*'},
               {'POS': 'PART', 'OP': '*'},
               {'POS': {'IN' : ['VERB', 'AUX']}, 'OP': '+'},
               {'POS': 'PART', 'OP': '?'},
               ]
    matcher = Matcher(nlp.vocab)
    matcher.add("Verb Phrase", None, pattern)
    matches = matcher(sent_doc)
    spans = [sent_doc[start:end] for _, start, end in matches]
    return filter_spans(spans)
    
    
def tense_of_verb(verb_str):
    """
    Identifies the verb tense of a word, and returns it in a tuple along with its base word.
    @param verb_str: a str containing a verb
    @return: a tuple t, where t[0] is 'AUX' if the verb is a special auxiliary verb, 
        is '?' if the verb tense cannot be recognized, and otherwise is 'VBD', 'VBP', or 'VBZ',
        which correspond to the Penn Treebank P.O.S. tags for past tense, non-3rd person present 
        tense, and 3rd person present tense.
    """
    aux_verbs = ['am', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 
                'do', 'does', 'did', 'will', 'would', 'shall', 'should', 
                'may', 'might', 'must', 'can', 'could', 'ought']
    if verb_str.lower() in aux_verbs:
        return ('AUX', verb_str)
    lemm_str = getLemma(verb_str, upos='VERB')[0]
    if verb_str in getInflection(lemm_str, tag='VBD'):
        return ('VBD', lemm_str)
    elif verb_str in getInflection(lemm_str, tag='VBP'):
        return ('VBP', lemm_str)
    elif verb_str in getInflection(lemm_str, tag='VBZ'):
        return ('VBZ', lemm_str)
    else:
        return ('?', lemm_str)

def negate(sent_doc, verb_slices, to_neg):
    """
    @param sent_doc: A spacy doc containing a sentence.
    @param verb_slices: result of calling extract_verb_slices on sent_doc.
    @param to_neg: a list of booleans. to_neg[i] is True if ith verb should be negated
        and False if it shouldn't be. len(to_neg) should equal the number of verbs in the sentence.
    @return: a string containing the resulting sentence.
    """
    negated_sent = []
    wi = 0;
    vi = 0;
    while wi < len(sent_doc):
        if vi >= len(verb_slices) or wi != verb_slices[vi][0].i:
            negated_sent.append(sent_doc[wi].text)
            wi += 1
        #if wi == verb_slices[vi][0].i:
        else:
            if to_neg[vi]:

                neg = [token for token in verb_slices[vi] if token.dep_ == 'neg']
                aux = [token for token in verb_slices[vi] if token.dep_ in ['aux', 'auxpass']]
                verbs = [token for token in verb_slices[vi] if token.pos_ == 'VERB' or 
                    (token.pos_ == 'AUX' and token.dep_ in ['ROOT', 'ccomp', 'conj', 'xcomp'])]
                verb = verbs[0]

                if neg:
                    for token in verb_slices[vi]:
                        if token.dep_ != 'neg':
                            negated_sent.append(token.text)
                elif aux:
                    for token in verb_slices[vi]:
                        negated_sent.append(token.text)
                        if token == aux[0]:
                            negated_sent.append('not')
                else:
                    tense, base = tense_of_verb(verb.text)
                    if tense == 'AUX':
                        negated_sent.extend([verb.text, 'not'])
                    elif tense == 'VBD':
                        negated_sent.extend(['did', 'not', base])
                    elif tense == 'VBP':
                        negated_sent.extend(['do', 'not', base])
                    elif tense == 'VBZ':
                        negated_sent.extend(['does', 'not', base])
                    else:
                        negated_sent.extend(['do', 'not', base])
            else:
                negated_sent.extend([token.text for token in verb_slices[vi]])
            wi = verb_slices[vi][-1].i + 1
            vi += 1
    return negated_sent

def qualify(sent_str):
    """
    @param sent_str: a string containing a sentence.
    @return: a list containing all alternate forms of the sentence.
    """
    sent_doc = nlp(sent_str)
    if sent_doc[-1].text != "." and sent_doc[-1].text != "!":
        return []

    verb_slices = extract_verb_slices(sent_doc)
    if not verb_slices:
        return []

    combos = [[]]
    for i in range(len(verb_slices)):
        off = [l + [0] for l in combos]
        on  = [l + [1] for l in combos]
        combos = off + on

    sent_lists = [negate(sent_doc, verb_slices, to_neg) for to_neg in combos]
    sents = [sent_join(s) for s in sent_lists]
    return sents

def sent_join(sent_list):
    """
    @param sent_list: a list of strs, each representing a word or punctuation.
    @return: a string with the full sentence, with spaces between words when needed.
    """
    PUNCT = [".", "?", "!", ",", "-", "(", ")", "[", "]", "'", '"']
    result = sent_list[0]
    for i in range(1, len(sent_list)):
        token = sent_list[i]
        if any(p in token for p in PUNCT):
            result += token
        else:
            result += " " + token
    return result

def changepov(sent_str):
    sent_doc = nlp(sent_str)
    sent_list = [token.text for token in sent_doc]
    
    for token in sent_doc:
        if token.lower_ in ['i', 'me']:
            if token.i == 0:
                sent_list[token.i] = 'You'
            else:
                sent_list[token.i] = 'you'
            if token.dep_ == 'nsubj':
                if token.head.lower_ == 'am':
                    sent_list[token.head.i] = 'are'
                elif token.head.lower_ == 'was':
                    sent_list[token.head.i] = 'were'
        elif token.lower_ == 'you':
            if token.dep_ == 'nsubj':
                sent_list[token.i] = 'I'
                if token.head.lower_ == 'are':
                    sent_list[token.head.i] = 'am'
                elif token.head.lower_ == 'were':
                    sent_list[token.head.i] = 'was'
            else:
                sent_list[token.i] = 'me'
    return sent_join(sent_list)
