#!/usr/bin/env python3

import Asking, Parser
import spacy
import sys
import en_core_web_sm

class GenerateQuestions(object):

	def __init__(self, textFile):
		self.nlp = en_core_web_sm.load()
		self.asker = Asking.Asking(textFile)
		self.parser = Parser.Parser(textFile)

	# add style check function (trim whitespace)

	# Refine questions by deleting words of a sentence surrounded by commas or
	# making them into their own sentence
	def splitCommas(self, sentence, root, ner_tags):
		if "," not in sentence:
			return sentence
		deleteParts = set()
		splitSentence = sentence.split(",")[1:]

		# if root is not in part surrounded by commas and part is not long,
		# delete part
		# edge case: if there are words like because, since, which, due to
		for part in splitSentence:
			partLen = len(part.split())
			if partLen < 5 and root not in part:
				if ('because' not in part) and ('since' not in part) and \
						('which' not in part) and ('due to' not in part):
					for tag in ner_tags:
						if tag not in part:
							deleteParts.add(part)
		# delete unnecessary parts from original sentence
		for part in deleteParts:
			sentence = sentence.replace(part, "")
		return sentence

	def checkSentenceType(self, sentence, dep_dict, ner_tag_dict, root):
		possible_types = set()
		if ("TIME" in ner_tag_dict.values()) or (
				"DATE" in ner_tag_dict.values()):
			possible_types.add("When")
		if ("PERSON" in ner_tag_dict.values()):
			possible_types.add("Who")
		if ("FAC" in ner_tag_dict.values()) or (
				"ORG" in ner_tag_dict.values()) or (
				"LOC" in ner_tag_dict.values()) or (
				"GPE" in ner_tag_dict.values()):
			possible_types.add("Where")
		if ("MONEY" in ner_tag_dict.values()):
			possible_types.add("How much")
		if ("DATE" in ner_tag_dict.values()):
			for k in ner_tag_dict.keys():
				if ner_tag_dict[k] == "DATE" and not k.isnumeric():
					possible_types.add("How long")
		if ("CARDINAL" in ner_tag_dict.values()):
			for k in ner_tag_dict.keys():
				if ner_tag_dict[k] == "CARDINAL" and not k.isnumeric():
					possible_types.add("How many")
		if ("because" in sentence) or ("due to" in sentence) or (
				"Due to" in sentence) or ("since" in sentence):
			possible_types.add("Why")
		aux_verbs = {"are", "is", "was", "were", "shall", "do", "does", "did",
					 "can", "could", "have", "need", "should", "will", "would",
					 "must", "may", "might", "cannot"}
		if root in aux_verbs:
			possible_types.add("What")
		for dep in dep_dict.values():
			vals = {'nsubj', 'nsubjpass', 'auxpass'}
			if dep[0] in vals:
				possible_types.add("What")
		return possible_types

	def generateQuestions(self, limit):
		possible_questions = set()
		for sentence in self.parser.text:
			# print("SENTENCE: ", sentence)

			nlp_doc = self.nlp(sentence)
			pos_tags = self.parser.pos_tag_sentence(sentence)
			token_dict, root = self.parser.dependency_dict(nlp_doc)
			ner_tags = self.parser.ner_tag_sentence(sentence)

			type_dict = {"How many": self.asker.howManyQ(sentence, ner_tags,
												token_dict, pos_tags, root),
						 "Who": self.asker.whoQ(sentence, ner_tags, root),
						 "How much": self.asker.howMuchQ(sentence, nlp_doc, ner_tags,
													  token_dict, root, pos_tags),
						 "How long": self.asker.howLongQ(sentence, ner_tags, token_dict,
														pos_tags, root),
						 "Why": self.asker.whyQ(sentence, nlp_doc, ner_tags, token_dict,
											 pos_tags, root),
						 "Where": self.asker.whereQ(sentence, token_dict, pos_tags),
						 "What": self.asker.whatQ(sentence, token_dict, root),
						 "When": self.asker.whenQ(sentence, ner_tags, root, nlp_doc,
											   pos_tags)}

			# generate question outputs
			possible_types = self.checkSentenceType(sentence, token_dict,
													ner_tags, root)
			#print(sentence)
			#print(possible_types)
			for type in possible_types:
				try:
					question = type_dict[type]
					if self.isValidQuestion(question):
						# print(f"VALID Q: ({type})", question)
						possible_questions.add(question)
						if len(possible_questions) == limit: return possible_questions
				except:
					# print("ERROR HERE: ", type)
					continue

				# check if binary question is possible
			try:
				binary_output = self.asker.binaryQ(sentence, ner_tags, pos_tags,
											   nlp_doc, root, token_dict)
				if self.isValidQuestion(binary_output):
					# print("BINARY Q: ", binary_output)
					possible_questions.add(binary_output)
					if len(possible_questions) == limit: return possible_questions
			except:
				continue

			# limit amount of questions to be generated
			if len(possible_questions) >= limit:
				return possible_questions
		return possible_questions

	# check if generated question is valid
	def isValidQuestion(self, question):
		return question != None and len(question) > 0

if __name__ == "__main__":
	input_file = sys.argv[1]
	N = int(sys.argv[2])

	generator = GenerateQuestions(input_file)
	questions = generator.generateQuestions(N)
	for q in questions:
		print(q)
