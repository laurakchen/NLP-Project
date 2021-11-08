import nltk
from nltk.tokenize import sent_tokenize
import spacy
from nltk.stem import WordNetLemmatizer

nlp = spacy.load('en_core_web_sm')
lemmatizer = WordNetLemmatizer()
textfile = "data/set4/a7.txt"

#put entire text file into a list of sentences
text = []
with open(textfile, "r") as f:
	for line in f:
		line = line.split('. ')
		if len(line) != 0:
			temp = line[0].strip('\n')
			if len(temp) != 0:
				text.append(temp)

def pos_tag_lst(text):
	#list of sentences
	POS_tag_dict = dict()
	for i,line in enumerate(text):
		tags = []
		doc = nlp(str(line))
		for token in doc:
			tags.append((token.text, token.pos_, token.tag_, token.dep_, token.is_stop))
		if len(tags) != 0:
			POS_tag_dict[i] = tags
	return POS_tag_dict

def pos_tag_sentence(sentence):
	#list of sentences
	POS_tag_dict = dict()
	text = sentence.split()
	for line in text:
		tags = []
		doc = nlp(str(line))
		for token in doc:
			tags.append((token.pos_, token.tag_, token.dep_, token.is_stop, ))
		if len(tags) != 0:
			POS_tag_dict[token.text] = tags[0]
	return POS_tag_dict

#Token dict
def dependency_dict(doc):
	out = dict()
	root = ''
	for token in doc:
		out[token.text] = (token.dep_, token.head.text, token.head.pos_,[child for child in token.children])
		if token.dep_ == "ROOT":
			root = token.text
	return out, root

# NER tagging
def ner_tag(text):
	NER_tag_dict = dict()
	for i,line in enumerate(text):
		tags = []
		doc = nlp(str(line))

		for ent in doc.ents:
			# print(ent.text +'-' + ent.label_ + '\n')
			tags.append(ent.text +'-' + ent.label_)
		if len(tags) != 0:
			NER_tag_dict[i] = tags
	return NER_tag_dict

def ner_tag_sentence(sentence):
	doc = nlp(str(sentence))
	NER_tag_dict = dict()
	tags = []
	for ent in doc.ents:
		# print(ent.text +'-' + ent.label_ + '\n')
		NER_tag_dict[ent.text] = ent.label_
	return NER_tag_dict


#check tense of verb
def check_tense(root, pos_dict):
	tag = pos_dict[root][1]
	if tag == "VB":
		return "do"
	elif tag == "VBD":
		return "did"
	elif tag == "VBG":
		return "doing"
	elif tag == "VBN":
		return "done"
	elif tag == "VBP":
		return "do"
	elif tag == "VBZ":
		return "does"
	else:
		return None

# return dictionary of lemmas in sentence
def getTokenLemma(nlp_doc):
	lemmas = {}
	for token in nlp_doc:
		lemmas[str(token)] = token.lemma_
	return lemmas

aux_verbs = ["are", "is", "was", "were", "shall", "do", "does", "did",
			 "can", "could", "have", "need", "should", "will", "would", "must",
			 "may", "might", "cannot"]

# what Question
def whatQ(sentence, dep_dict, root):
	output = ''
	if root in aux_verbs:
		output += f"What {root} "
		seenRoot = False
		for n in sentence.split():
			if n == root:
				seenRoot = True
			elif seenRoot:
				output += n + " "
		return output[:-2] + "?"
	else:
		pos_tags = pos_tag_sentence(sentence)
		lemmas = getTokenLemma(nlp(sentence))
		verb_tense = check_tense(root, pos_tags)
		if verb_tense != None:
			output += f"What {verb_tense} "
		else:
			output += "What does " # edge case (some verbs are not captured)
		nsubj_word = None
		for n in dep_dict:
			if dep_dict[n][0] == "nsubj" and nsubj_word == None:
				nsubj_word = n
				# account for word dependencies before nominal subject
				if dep_dict[n][3] != []:
					for prev in dep_dict[n][3]:
						output += str(prev).lower() + " "
				output += f"{n} {lemmas[root]} " # add root after nominal subject
		post_root_nouns = []
		for pos in pos_tags:
			if pos != root and pos != nsubj_word:
				if pos_tags[pos][0] == "NOUN" or pos_tags[pos][0] == "PROPN":
					post_root_nouns.append(pos)
					break
		# add nouns/propositions after root
		if len(post_root_nouns) == 1:
			output += post_root_nouns[0] + " "
		output = output[:-1] + "?"
		return output

# where question that includes 'where' in sentence
def whereQ(sentence, dep_dict, root):
	output = ''
	verbs = ['was', 'is', 'were']
	foundVerb = False
	foundVerbInd = 0
	# find tense
	pos_tags = pos_tag_sentence(sentence)
	foundWhereInd = 0
	whereInd = 0
	tense = None
	for word in sentence.split():
		if word == 'where':
			foundWhereInd = whereInd
			verb = dep_dict[word][1]
			if pos_tags[verb][0] == 'VERB':
				tense = check_tense(verb, pos_tags)
			elif verb in verbs: # if tense is was, is, were
				tense = verb
				foundVerb = True
				foundVerbInd = sentence.split().index(verb)
			break
		whereInd += 1
	if tense == None: # not able to create question from sentence
		return "No question"
	output += f'Where {tense} '
	ind = foundWhereInd
	if foundVerb:
		ind = foundVerbInd
	for word in sentence.split()[ind+1:]:
		output += word + " "
	return output[:-2] + "?"

# test cases
test_sentence1 = "Harry Potter and The Prisoner of Azkaban is a 2004 fantasy film."
test_sentence2 = "Peppy tells Zimmer to get tea."
test_sentence3 = "Sirius sends Harry a Firebolt broom."

dep_dict1, root1 = dependency_dict(nlp(test_sentence1))
dep_dict2, root2 = dependency_dict(nlp(test_sentence2))
dep_dict3, root3 = dependency_dict(nlp(test_sentence3))

print(whatQ(test_sentence1, dep_dict1, root1))
print(whatQ(test_sentence2, dep_dict2, root2))
print(whatQ(test_sentence3, dep_dict3, root3))