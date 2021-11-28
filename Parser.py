#!/usr/bin/env python3
import nltk
from nltk.tokenize import sent_tokenize
import spacy
import en_core_web_sm

class Parser(object):

	def __init__(self, textFile):
		self.nlp = en_core_web_sm.load()
		# put entire text file into a list of sentences
		self.text = self.get_text(textFile)

	def get_text(self, textFile):
		text = []
		with open(textFile, "r") as f:
			for line in f:
				if len(line) > 100:
					tmp_lst = line.split(",")
					for list in tmp_lst:
						text += sent_tokenize(list)
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
				tags.append(ent.text + '-' + ent.label_)
			if len(tags) != 0:
				NER_tag_dict[i] = tags
		return NER_tag_dict

	def ner_tag_sentence(self, sentence):
		doc = self.nlp(str(sentence))
		NER_tag_dict = dict()
		for ent in doc.ents:
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
	'''
	return the correct style of a sentence:
	first letter capitalized, only 1 space between each word
	no space between final word and punctuation
	lower-cased words without NER tags
	'''
	def check_style(self, sentence):
		if len(sentence) <= 0:
			return sentence
		result = ""
		if sentence[-1] == "?":
			result = " ".join(sentence.split())
		else:
			if sentence[-1] in ".!() ":
				sentence = sentence[:-1]
			result = " ".join(sentence.split()) + "?"
		result = result[0].upper() + result[1:]
		return result





