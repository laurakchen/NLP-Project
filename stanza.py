#stanza.py

import stanza

nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos')
doc = nlp('Barack Obama was born in Hawaii.')
nlp = spacy.load('en_core_web_sm')