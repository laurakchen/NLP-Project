#!/usr/bin/env python3
import sys
import time
import Answering, Parser
import spacy
from nltk.tokenize import sent_tokenize
import en_core_web_sm


class GenerateAnswers(object):

	def __init__(self, textfile, questions):
		self.nlp = spacy.load("en_core_web_sm")
		self.answer = Answering.Answering(textfile)
		self.parser = Parser.Parser(textfile)
		self.text = self.parser.text
		self.questions = self.read_questions(questions)

	def read_questions(self, questions):
		question = []
		with open(questions, "r") as f:
			for line in f:
				question = question + sent_tokenize(line)
		return question

	#return all answers
	def getAnswer(self):
		all_answer = []
		for question in self.questions:
			if self.answer.check_binary_question(question):
				answer = self.answer.binary_answer(question)
				answer = self.answer.get_answer(answer, question)
			else:
				answer = self.answer.get_answer_from_text(question)
				answer = self.answer.get_answer(answer, question)
			all_answer.append(answer)
		return all_answer

	def displayAnswer(self, all_answer):
		for answer in all_answer:
			print(answer)

if __name__ == "__main__":
	input_file = sys.argv[1]
	question_file = sys.argv[2]

	generator = GenerateAnswers(input_file, question_file)
	answers = generator.getAnswer()
	generator.displayAnswer(answers)

