import spacy
import lemminflect
from lemminflect import getLemma, getInflection
nlp = spacy.load('en_core_web_sm')

def extract_verb_slices(sent_doc):
    """
    Slices the verb and its aux/neg children from sent_doc.
    @param sent_doc: a spacy doc, containing a sentence.
    @return: a list of spacy spans, each representing a different verb and its aux/neg children.
    """
    root = None
    for token in sent_doc:
        if token.dep_ == 'ROOT':
            root = token
            root.pos_ = 'VERB'

    queue = [root]
    verbs = [root]
    while queue:
        v = queue.pop(0)
        for token in v.children:
            if token.dep_ in ['ccomp', 'conj']:
                queue.append(token)
                verbs.append(token)
                token.pos_ = 'VERB'
    
    verb_slices = []
    for verb in verbs:
        start, end = verb.i, verb.i + 1
        for token in sent_doc:
            if token.head == verb:
                if token.dep_ == 'aux' or token.dep_ == 'auxpass' or token.dep_ == 'neg':
                    if token.i < start:
                        start = token.i
                    elif token.i + 1 > end:
                        end = token.i + 1
        verb_slices.append(sent_doc[start:end])
    return verb_slices
    


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
                verbs = [token for token in verb_slices[vi] if token.pos_ == 'VERB']
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
        return [False]

    verb_slices = extract_verb_slices(sent_doc)
    if not verb_slices:
        return [False]

    combos = [[]]
    for i in range(len(verb_slices)):
        off = [l + [0] for l in combos]
        on  = [l + [1] for l in combos]
        combos = off + on

    sent_lists = [negate(sent_doc, verb_slices, to_neg) for to_neg in combos]
    sents = []
    for sl in sent_lists:
        if sl[-1] in [".", "!", "?"]:
            s = " ".join(sl[:-1]) + sl[-1]
        else:
            s = " ".join(sl)
        sents.append(s)
    return sents
