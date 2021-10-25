#Question generating System

import nltk
from nltk.tokenize import sent_tokenize
import spacy

nlp = spacy.load('en_core_web_sm')
textfile = "data/set4/a7.txt"
doc1 = nlp("Harry Potter and the Prisoner of Azkaban is a 2004 fantasy film directed by Alfonso Cuarón and distributed by Warner Bros.")


#Binary question 
def get_Token_dict(doc1):
	out = dict()
	for token in doc1:
		out[token.text] = (token.dep_, token.head.text, token.head.pos_,[child for child in token.children])
	return out

token_Dict = get_Token_dict(doc1)
print(token_Dict)


