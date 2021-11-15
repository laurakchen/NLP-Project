import nltk
from nltk.tokenize import sent_tokenize
import spacy
import numpy as np

class Parser(object):

	def __init__(self, textFile):
		self.nlp = spacy.load('en_core_web_sm')
		# put entire text file into a list of sentences
		self.text = self.get_text(textFile)

	def get_text(self, textFile):
		text = []
		with open(textFile, "r") as f:
			for line in f:
				text = text + sent_tokenize(line)
		return text

	def pos_tag_lst(self, text):
		# list of sentences
		POS_tag_dict = dict()
		for i, line in enumerate(text):
			tags = []
			doc = self.nlp(str(line))
			for token in doc:
				tags.append((token.text, token.pos_, token.tag_, token.dep_,
							 token.is_stop))
			if len(tags) != 0:
				POS_tag_dict[i] = tags
		return POS_tag_dict

	def pos_tag_sentence(self, sentence):
		# list of sentences
		POS_tag_dict = dict()
		text = sentence.split()
		for line in text:
			tags = []
			doc = self.nlp(str(line))
			for token in doc:
				tags.append(
					(token.pos_, token.tag_, token.dep_, token.is_stop,))
			if len(tags) != 0:
				POS_tag_dict[token.text] = tags[0]
		return POS_tag_dict

	# def pos_tag_sentence(self, sentence):
	# 	# list of sentences
	# 	POS_tag_dict = dict()
	# 	text = sentence.split()
	# 	for i, line in enumerate(text):
	# 		tags = []
	# 		doc = self.nlp(str(line))
	# 		for token in doc:
	# 			tags.append((token.text, token.pos_, token.tag_, token.dep_,
	# 						 token.is_stop,))
	# 		if len(tags) != 0:
	# 			POS_tag_dict[i] = tags
	# 	return POS_tag_dict

	# Token dict
	def dependency_dict(self, doc):
		out = dict()
		root = ''
		for token in doc:
			out[token.text] = (token.dep_, token.head.text, token.head.pos_,
							   [child for child in token.children])
			if token.dep_ == "ROOT":
				root = token.text
		return out, root

	# NER tagging
	def ner_tag(self, text):
		NER_tag_dict = dict()
		for i, line in enumerate(text):
			tags = []
			doc = self.nlp(str(line))

			for ent in doc.ents:
				# print(ent.text +'-' + ent.label_ + '\n')
				tags.append(ent.text + '-' + ent.label_)
			if len(tags) != 0:
				NER_tag_dict[i] = tags
		return NER_tag_dict

	def ner_tag_sentence(self, sentence):
		doc = self.nlp(str(sentence))
		NER_tag_dict = dict()
		tags = []
		for ent in doc.ents:
			# print(ent.text +'-' + ent.label_ + '\n')
			NER_tag_dict[ent.text] = ent.label_
		return NER_tag_dict

	# check tense of verb
	def check_tense(self, root, pos_dict):
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
	def getTokenLemma(self, nlp_doc):
		lemmas = {}
		for token in nlp_doc:
			lemmas[str(token)] = token.lemma_
		return lemmas
