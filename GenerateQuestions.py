import Asking, Parser
import spacy

class GenerateQuestions(object):

	def __init__(self):
		textfile = "test.txt"
		self.nlp = spacy.load('en_core_web_sm')
		self.asker = Asking.Asking(textfile)
		self.parser = Parser.Parser(textfile)
		self.POS_tag_dict = self.parser.pos_tag_lst(self.parser.text)
		self.ner_tags = self.parser.ner_tag(self.parser.text)
		print("done with initializing")

	def generateQuestions(self, limit):
		possible_questions = set()
		for sentence in self.parser.text:
			print(sentence)
			nlp_doc = self.nlp(sentence)
			pos_tags = self.parser.pos_tag_sentence(sentence)
			token_dict, root = self.parser.dependency_dict(nlp_doc)
			ner_tags = self.parser.ner_tag_sentence(sentence)
			# verb_tense = self.parser.check_tense(root, pos_tags)
			lemma_dict = self.parser.getTokenLemma(nlp_doc)
			how_many_output = self.asker.howManyQ(sentence, ner_tags, token_dict,
							pos_tags, root)
			binary_output = self.asker.binaryQ(sentence, root)
			who_output = self.asker.whoQ(sentence, ner_tags, token_dict)
			how_much_output = self.asker.howMuchQ(sentence, nlp_doc, ner_tags,
												  token_dict, root, pos_tags)
			how_often_output = self.asker.howOftenQ(sentence, ner_tags, token_dict,
													pos_tags, root)
			why_output = self.asker.whyQ(sentence, nlp_doc, ner_tags, token_dict,
										 pos_tags, root)
			where_output = self.asker.whereQ(sentence, token_dict, pos_tags)
			what_output = self.asker.whatQ(sentence, token_dict, root, pos_tags,
										   lemma_dict)
			when_output = self.asker.whenQ(sentence, ner_tags, root, nlp_doc,
										   pos_tags)
			curr_questions = [how_many_output, binary_output, who_output,
							  how_much_output, how_often_output, why_output,
							  where_output, what_output, when_output]
			print("got current questions!")
			# if current questions are valid, add to list of possible questions
			for q in curr_questions:
				if self.isValidQuestion(q):
					print(q)
					possible_questions.add(q)
			# limit amount of questions to be generated
			if len(possible_questions) >= limit:
				return possible_questions
		return possible_questions

	# check if generated question is valid
	def isValidQuestion(self, question):
		return question != None and len(question) > 0

generator = GenerateQuestions()
generator.generateQuestions(50)