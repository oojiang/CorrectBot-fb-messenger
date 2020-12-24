import spacy
import lemminflect
from lemminflect import getLemma, getInflection
nlp = spacy.load('en_core_web_sm')

def extract_verb_phrase(sent_doc):
    """
    Slices the verb and its aux/neg children from sent_doc.
    @param sent_doc: a spacy doc, containing a sentence.
    @return: a spacy span, or False if the verb phrase could not be extracted.
    """
    verbi = -1
    for token in sent_doc:
        if token.dep_ == 'ROOT':
            verbi = token.i
    if verbi == -1:
        return False
    start, end = verbi, verbi + 1
    for token in sent_doc:
        if token.dep_ == 'aux' or token.dep_ == 'auxpass' or token.dep_ == 'neg':
            if token.head == sent_doc[verbi]:
                if token.i < start:
                    start = token.i
                elif token.i + 1 > end:
                    end = token.i + 1
    return sent_doc[start:end]

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

def negate(sent_str):
    """
    Returns the negation of a simple sentence. 
    @param sent_str: a str containing a sentence.
    @return: the negation of sent_str. 
        Returns False if the sentence could not be negated (e.g. the sentence is a question)
    """

    sent_doc = nlp(sent_str)

    if sent_doc[-1].text != "." and sent_doc[-1].text != "!":
        return False

    verb_slice = extract_verb_phrase(sent_doc)

    if not verb_slice:
        return False

    negated_sent = ''
    first_neg, first_aux = (-1, -1), (-1, -1)
    root_verb = (-1, -1)
    verb_str = ''
    for token in verb_slice:
        if token.dep_ == 'neg' and first_neg == (-1, -1):
            first_neg = (token.idx, sent_doc[token.i + 1].idx)
        elif (token.dep_ == 'aux' or token.dep_ == 'auxpass') and first_aux == (-1, -1):
            first_aux = (token.idx, sent_doc[token.i + 1].idx)
        elif token.dep_ == 'ROOT':
            root_verb = (token.idx, sent_doc[token.i + 1].idx)
            verb_str = token.text
    if first_neg != (-1, -1):
        negated_sent = sent_str[:first_neg[0]] + sent_str[first_neg[1]:]
    elif first_aux != (-1, -1):
        negated_sent = sent_str[:first_aux[1]] + ' not ' +  sent_str[first_aux[1]:]
    else:
        assert len(verb_slice) == 1
        tense, base = tense_of_verb(verb_str)
        if tense == 'AUX':
            negated_sent = sent_str[:root_verb[1]] + ' not ' + sent_str[root_verb[1]:]
        elif tense == 'VBD':
            negated_sent = sent_str[:root_verb[0]] + " didn't " + base + ' ' + sent_str[root_verb[1]:]
        elif tense == 'VBP':
            negated_sent = sent_str[:root_verb[0]] + " don't " + base + ' ' + sent_str[root_verb[1]:]
        elif tense == 'VBZ':
            negated_sent = sent_str[:root_verb[0]] + " doesn't " + base + ' ' + sent_str[root_verb[1]:]
        else:
            negated_sent = sent_str[:root_verb[0]] + " don't " + base + ' ' + sent_str[root_verb[1]:]
    negated_sent = negated_sent.strip()
    negated_sent = ' '.join(negated_sent.split())
    if negated_sent[-2:] == " .":
        negated_sent = negated_sent[0:-2] + negated_sent[-1:]
    return negated_sent

def identify_clauses(sent_doc):
    """
    Returns a list of word indeces where each clause starts.
    """
