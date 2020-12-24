import spacy
from spacy import displacy

nlp = spacy.load('en_core_web_sm')

def print_text(text):
    doc = nlp(text)
    for token in doc:
        print (token.text, token.head, token.dep_)
    print()

samp_text = 'The cat ran to the dog.'
print_text(samp_text)

complex_text = 'I said that the cat ran to the dog.'
print_text(complex_text)

complex2_text = 'John fixed the vase that he broke.'
print_text(complex2_text)

negative_text = 'The cat did not run to the dog.'
print_text(negative_text)

is_text = 'That is a good computer.'
print_text(is_text)

mult_aux_text = 'Those claims should have been being examined a lot lately.'
print_text(mult_aux_text)

mult_aux_pass_text = 'Fred may be being judged to have been deceived by the explanation.'
print_text(mult_aux_pass_text)

possession_text = "Bob's fish eats food."
print_text(possession_text)

mult_clause_text = "Bob ate the apple, while Alice ate the orange."
print_text(mult_clause_text)

mult_clause_text2 = "Under the tree lay a pride of lions, and elephants slept and ate."

mult_verbs_text = "Yesterday Donna watched a movie, cleaned her apartment and was making lunch."

displacy.serve(nlp(mult_clause_text2), style='dep')
