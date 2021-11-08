import nltk
from nltk.tokenize import sent_tokenize
import spacy
from nltk.stem import WordNetLemmatizer
import re
import Parser

class Asking(object):

	def __init__(self, textFile):
		self.nlp = spacy.load('en_core_web_sm')
		self.lemmatizer = WordNetLemmatizer()
		self.auxiliary_verbs = ["am", "is", "are", "was", "were", "shall", "do",
								"does", "did","can", "could", "have", "need",
								"should", "will", "would"]
		self.textFile = textFile
		self.parser = Parser.Parser(self.textFile)

	# input: a single sentence, with its dependency dict and root word
	def binaryQ(self, sentence, token_dict, root):
		output = ''
		if root in self.auxiliary_verbs:
			output += root.capitalize() + ' '
		for k in sentence.split():
			if k != root:
				output += k + ' '
		output = output[:-2] + '?'
		return output

	# input: a single sentence, and its ner tag dict and dependency dict
	# Who Question
	def whoQ(self, sentence, ner_tag_dict, dependency_dict):
		# find PERSON tag
		theName = ''
		output = ''
		for k in ner_tag_dict.keys():
			if ner_tag_dict[k] == 'PERSON':
				# check if is a subject
				names = k.split()
				for n in names:
					if dependency_dict[n][0] == 'nsubj':
						theName = k
		output = sentence.replace(theName, 'who')
		output = output[:-1] + "?"
		output = output[0].upper() + output[1:]
		return output

	# input: a single sentence, and its ner tag dict and dependency dict
	# How much Question
	# The film was produced by La Petite Reine and ARP Sélection for 13.47 million dollars.
	# How much was the film produced by La Petite Reine and ARP Sélection?
	def howMuchQ(self, sentence, doc, ner_tag_dict, dependency_dict, root, pos_dict):
		theMoney = ""
		output = ""
		theSubj = ""
		for k in ner_tag_dict.keys():
			if ner_tag_dict[k] == 'MONEY':
				theMoney = k
		# check passive tense
		sentence_lst = sentence.split()
		root_ind = sentence_lst.index(root)
		root_token = doc[root_ind]
		if root_ind != 0:
			word_in_front_of_root = sentence_lst[root_ind - 1]
			# if it's passive tense
			if dependency_dict[word_in_front_of_root][0] == 'auxpass':
				root_aux = word_in_front_of_root
				output += 'How much ' + root_aux + ' '
				for n in dependency_dict:
					if dependency_dict[n][0] == 'nsubjpass':
						theSubj = n
				words_before_subj = dependency_dict[theSubj][-1]
				if len(words_before_subj) != 0:
					output += str(words_before_subj[0]).lower() + ' '
				output += theSubj + "?"

			else:  # if it's not passive tense
				for n in dependency_dict:
					if dependency_dict[n][0] == 'nsubj':
						theSubj = n
				output += 'How much '
				# check tense
				tense = self.parser.check_tense(root, pos_dict)
				if tense != None:
					output += tense + ' '
					# check subject
					for n in dependency_dict:
						if dependency_dict[n][0] == 'nsubj':
							theSubj = str(n)
					words_before_subj = dependency_dict[theSubj][-1]
					if len(words_before_subj) != 0:
						for t in words_before_subj:
							output += str(t).lower() + " "
					output += theSubj + ' ' + root_token.lemma_ + "?"
				else:
					return None
		return output

	def howManyQ(self, sentence, ner_tag_dict, dependency_dict, pos_tag_sentence,
				 root):
		token_Dict, root = self.parser.dependency_dict(self.nlp(sentence))
		Number = ""
		output = ""
		clause = ""
		for k in ner_tag_dict.keys():
			if ner_tag_dict[k] == 'CARDINAL':
				Number = k
		if Number == "": return
		sentence_lst = sentence.split()
		for seg in sentence.split(',', 1):
			if Number in seg: clause = seg
		if root not in clause: return
		clause_lst = clause.split()
		root_ind = clause_lst.index(root)
		number_ind = clause_lst.index(Number)
		if number_ind < root_ind:
			output = "How many" + sentence.split(Number, 1)[1][:-1]
		else:
			if root_ind != 0:
				word_in_front_of_root = sentence_lst[root_ind - 1]
				# if it's passive tense
				if token_Dict[word_in_front_of_root][0] == 'auxpass':
					middle = clause[clause.find(root): clause.find(Number)]
					output = "How many" + clause.split(Number, 1)[1][
										  :-1] + " " + word_in_front_of_root + " " + \
							 clause.split(word_in_front_of_root, 1)[
								 0].lower() + " " + middle
				# if it's not passive tense
				else:
					verb = clause[
						   clause.find(root): clause.find(root) + len(root)]
					# if it's past tense
					if pos_tag_sentence(root)[0][0][2] in ("VBD", "VBN"):
						output = "How many" + clause.split(Number, 1)[1][
											  :-1] + " did " + \
								 clause.split(Number, 1)[0][0].lower() + \
								 clause.split(Number, 1)[0][
								 1:clause.find(root)] + self.nlp(verb)[0].lemma_
					# if it's not past tense
					else:
						output = "How many" + clause.split(Number, 1)[1][
											  :-1] + " does " + \
								 clause.split(Number, 1)[0][0].lower() + \
								 clause.split(Number, 1)[0][
								 1:clause.find(root)] + self.nlp(verb)[0].lemma_
		output = ' '.join(output.split()) + "?"
		return output

	def howOftenQ(self, sentence, ner_tag_dict, dependency_dict, pos_tag_sentence,
				  root):
		token_Dict, root = self.parser.dependency_dict(self.nlp(sentence))
		date = ""
		output = ""
		clause = ""
		sentence = sentence[:-1]
		for k in ner_tag_dict.keys():
			if ner_tag_dict[k] == 'DATE':
				date = k
		if date == "": return
		date_lst = date.split()
		sentence_lst = sentence.split()
		root_lst_ind = sentence_lst.index(root)
		root_ind = sentence.index(root)
		date_ind = sentence.index(date)
		if date_ind < root_ind:
			word_in_front_of_root = sentence_lst[root_lst_ind - 1]
			if token_Dict[word_in_front_of_root][0] == 'auxpass':
				sentence_lst[root_lst_ind - 1] = sentence_lst[root_lst_ind - 2]
				sentence_lst[root_lst_ind - 2] = word_in_front_of_root
			else:
				sentence_lst[root_lst_ind] = self.nlp(root)[0].lemma_
				if pos_tag_sentence(root)[0][0][2] in ("VBD", "VBN"):
					sentence_lst.insert(root_lst_ind - 1, "did")
				else:
					sentence_lst.insert(root_lst_ind - 1, "does")
			for i in date_lst:
				sentence_lst.remove(i)
			output = "How long " + " ".join(sentence_lst)
		else:
			for seg in sentence.split(',', 1):
				if date in seg: clause = seg
			if root_ind != 0:
				word_in_front_of_root = sentence_lst[root_lst_ind - 1]
				word_after_root = sentence_lst[root_lst_ind + 1]
				prep_ind = sentence.index(word_after_root)
				if token_Dict[word_after_root][
					0] != 'prep': word_after_root = ""
				# if it's passive tense
				if token_Dict[word_in_front_of_root][0] == 'auxpass':
					output = "How long " + word_in_front_of_root + " " + \
							 clause.split(word_in_front_of_root, 1)[
								 0].lower() + sentence[root_ind:prep_ind + len(
						word_after_root)]
				else:
					# if it's past tense
					if pos_tag_sentence(root)[0][0][2] in ("VBD", "VBN"):
						output = "How long" + " did " + clause.split(root, 1)[
							0].lower() + self.nlp(root)[0].lemma_ + sentence[
															   root_ind + len(
																   root):prep_ind + len(
																   word_after_root)]
					# if it's not past tense
					else:
						output = "How long" + " does " + clause.split(root, 1)[
							0].lower() + self.nlp(root)[0].lemma_ + sentence[
															   root_ind + len(
																   root):prep_ind + len(
																   word_after_root)]
		output = ' '.join(output.split()) + "?"
		return output

	def whyQ(self, sentence, doc, ner_tag_dict, dependency_dict, pos_tag_dict, root):
		# A do sth Because B
		theSubj = ""
		output = ""
		theObj = ""
		sentence_lst = sentence.split()
		root_ind = sentence_lst.index(root)
		# check tense
		tense = self.parser.check_tense(root, pos_tag_dict)

		if "because" or "due to" or "Due to" in sentence:
			# check if passive tense:
			word_in_front_of_root = sentence_lst[root_ind - 1]
			if dependency_dict[word_in_front_of_root][0] == 'auxpass':
				root_aux = word_in_front_of_root
				for n in dependency_dict:
					if dependency_dict[n][0] == 'nsubjpass':
						words_before_subj = dependency_dict[n][-1]
						if len(words_before_subj) != 0:
							for t in words_before_subj:
								if str(t) not in ner_tag_dict.keys():
									theSubj += str(t).lower() + ' '
								else:
									theSubj += str(t) + ' '
						theSubj += n + " "
				output += "Why " + root_aux + " " + theSubj + doc[
					root_ind].text + "?"

			else:
				# not passive tense:
				# find subject
				for n in dependency_dict:
					if dependency_dict[n][0] == 'nsubj':
						# find determinant if there is one
						words_before_subj = dependency_dict[n][-1]
						if len(words_before_subj) != 0:
							for t in words_before_subj:
								theSubj += str(t) + ' '
						theSubj += n
						break
				# find object
				for n in dependency_dict:
					if dependency_dict[n][0] == 'dobj':
						# find determinant if there is one
						words_before_obj = dependency_dict[n][-1]
						if len(words_before_obj) != 0:
							for t in words_before_obj:
								theObj += str(t) + ' '
						theObj += n
						break

				# check tense
				tense = self.parser.check_tense(root, pos_tag_dict)
				# Get rid of things after because

				# Why + do/does/did sb do sth?
				output += "Why " + tense + " " + theSubj + " " + doc[
					root_ind].lemma_ + " " + theObj + "?"
		return output

	def whereQ(self, sentence, dep_dict, root):
		output = ''
		verbs = ['was', 'is', 'were']
		foundVerb = False
		foundVerbInd = 0
		# find tense
		pos_tags = self.parser.pos_tag_sentence(sentence)
		seenWhere = False
		foundWhereInd = 0
		whereInd = 0
		tense = None
		for word in sentence.split():
			if word == 'where':
				seenWhere = True
				foundWhereInd = whereInd
				verb = dep_dict[word][1]
				if pos_tags[verb][0] == 'VERB':
					tense = self.parser.check_tense(verb, pos_tags)
				elif verb in verbs:  # if tense is was, is, were
					tense = verb
					foundVerb = True
					foundVerbInd = sentence.split().index(verb)
				break
			whereInd += 1
		if tense == None:  # not able to create question from sentence
			return "No question"
		output += f'Where {tense} '
		ind = foundWhereInd
		if foundVerb:
			ind = foundVerbInd
		for word in sentence.split()[ind + 1:]:
			output += word + " "
		return output[:-2] + "?"

	# what Question
	def whatQ(self, sentence, dep_dict, root):
		aux_verbs = ["are", "is", "was", "were", "shall", "do", "does", "did",
					 "can", "could", "have", "need", "should", "will", "would",
					 "must", "may", "might", "cannot"]
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
			pos_tags = self.parser.pos_tag_sentence(sentence)
			lemmas = self.parser.getTokenLemma(self.nlp(sentence))
			verb_tense = self.parser.check_tense(root, pos_tags)
			if verb_tense != None:
				output += f"What {verb_tense} "
			else:
				output += "What does "  # edge case (some verbs are not captured)
			nsubj_word = None
			for n in dep_dict:
				if dep_dict[n][0] == "nsubj" and nsubj_word == None:
					nsubj_word = n
					# account for word dependencies before nominal subject
					if dep_dict[n][3] != []:
						for prev in dep_dict[n][3]:
							output += str(prev).lower() + " "
					output += f"{n} {lemmas[root]} "  # add root after nominal subject
			post_root_nouns = []
			for pos in pos_tags:
				if pos != root and pos != nsubj_word:
					if pos_tags[pos][0] == "NOUN" or pos_tags[pos][
						0] == "PROPN":
						post_root_nouns.append(pos)
						break
			# add nouns/propositions after root
			if len(post_root_nouns) == 1:
				output += post_root_nouns[0] + " "
			output = output[:-1] + "?"
			return output

	def whenQ(self, sentence, ner_tag_dict, dependency_dict, root, doc, pos_dict):
		# find DATE/TIME tag
		theDateTime = ''
		theVerb = ''
		output = ''
		aux = ''
		for k in ner_tag_dict.keys():
			if ner_tag_dict[k] == 'DATE' or ner_tag_dict[k] == 'TIME':
				theDateTime = k
		sentence_lst = sentence.split()
		root_ind = sentence_lst.index(root)
		root_token = doc[root_ind]
		prep = ['in ', 'on ']
		for p in prep: sentence = sentence.replace(p, '')
		for k in pos_dict.keys():
			if pos_dict[k][0][1] == 'AUX':
				aux = pos_dict[k][0][0]
		if aux == '':
			theVerb = root_token.lemma_
			output = 'When '
			sentence = sentence.replace(theDateTime, '')
			sentence = sentence.replace(root, theVerb)
			sentence = re.sub('[^A-Za-z0-9]+', ' ', sentence)
			sentence = sentence.lower()
			tense = self.parser.check_tense(root_ind, pos_dict)
			output += tense + ' ' + sentence
		else:
			sentence = sentence.replace(theDateTime, '')
			sentence = sentence.replace(aux, '')
			output = 'When ' + aux + ' ' + sentence
			output = output.lower()
		output = output[0].upper() + output[1:]
		output = output.split(" ")
		output = " ".join(output)
		output = output[0:len(output) - 1] + "?"
		return output