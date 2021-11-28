#!/usr/bin/env python3
import spacy
from nltk.stem import WordNetLemmatizer
import re
import Parser
import en_core_web_sm

class Asking(object):

	def __init__(self, textFile):
		self.nlp = en_core_web_sm.load()
		self.lemmatizer = WordNetLemmatizer()
		self.auxiliary_verbs = {"am", "is", "are", "was", "were", "shall", "do",
								"does", "did","can", "could", "have", "need",
								"should", "will", "would"}
		self.parser = Parser.Parser(textFile)

	# input: a single sentence, with its dependency dict and root word
	def binaryQ(self, sentence, ner_tag_dict, pos_tag_dict, nlp_doc, root, dep_dict):
		output = ''
		if root not in sentence:
			return
		split = sentence.split()
		if root + "," in split:
			rootInd = split.index(root + ',')
		else:
			rootInd = split.index(root)
		ner_tags = set()
		for ner_tag in ner_tag_dict:
			split_tag = ner_tag.split()
			for split_word in split_tag:
				ner_tags.add(split_word)
		if root in self.auxiliary_verbs:
			output += root.capitalize() + ' '
			for word in split[0:rootInd]:
				if word not in ner_tags:
					output += word.lower() + ' '
				else:
					output += word + ' '
			output += " ".join(split[rootInd + 1:])
			output = output[:-1] + '?'
			return output
		else:
			aux_verb = ""
			minDist = len(split)
			for word in split:
				if word in self.auxiliary_verbs:
					if abs(split.index(word) - rootInd) < minDist:
						minDist = split.index(word) - rootInd
						aux_verb = word
			if aux_verb != "":
				output += aux_verb.capitalize() + ' '
				auxInd = split.index(aux_verb)
				output += " ".join(
					split[0:auxInd])  # add everything before aux verb
				output += " " + root + " "
				output += " ".join(split[rootInd + 1:])
			else:
				# edge case where root and nearby words not in auxiliary verbs
				tense = self.parser.check_tense(root, pos_tag_dict)
				if tense == None: return
				if tense == "done" and len(root) > 2 and root[-2:] == 'ed':
					tense = "does"
				output += tense.capitalize() + ' '
				if "," in split[0]:
					first = split[0]
					if dep_dict[first[0:-1]][0] == 'advmod':
						output += split[rootInd - 1] + ' '
				elif dep_dict[split[0]][0] == 'advmod':
					output += split[rootInd - 1] + ' '
				else:
					output += " ".join(split[0:rootInd]) + ' '
				output += self.parser.getTokenLemma(nlp_doc)[root] + ' '
				output += " ".join(split[rootInd + 1:])
			split_output = output.split()
			if split_output[1] not in ner_tags:
				output = split_output[0] + ' ' + split_output[1].lower() + \
						 ' ' + " ".join(split_output[2:])
			output = output[:-1] + '?'
			return self.parser.check_style(output)

	def whoQ(self, sentence, ner_tag_dict, root):
		# find PERSON tag
		theName = ''
		output = ''
		if root not in sentence:
			return
		rootInd = sentence.index(root)
		minDist = len(sentence)
		for ner_tag in ner_tag_dict:
			if ner_tag_dict[ner_tag] == 'PERSON':
				tag_ind = sentence.index(ner_tag)
				if abs(tag_ind - rootInd) < minDist:
					minDist = abs(tag_ind - rootInd)
					theName = ner_tag
		if theName == '':
			return
		if "'" in theName:
			output = sentence.replace(theName, 'whose', 1)
		else:
			output = sentence.replace(theName, 'who', 1)
		output = output[:-1] + "?"
		output = output[0].upper() + output[1:]
		return self.parser.check_style(output)

	# input: a single sentence, and its ner tag dict and dependency dict
	# How much Question
	# The film was produced by La Petite Reine and ARP Sélection for 13.47 million dollars.
	# How much was the film produced by La Petite Reine and ARP Sélection?
	def howMuchQ(self, sentence, doc, ner_tag_dict, dependency_dict, root, pos_dict):
		theMoney = ""
		output = ""
		theSubj = ""
		all_sentence_lst = []
		for k in ner_tag_dict.keys():
			if ner_tag_dict[k] == 'MONEY':
				theMoney = k
		# check passive tense
		# if len(sentence) > 100:
		# 	all_sentence_lst = sentence.split(",")
		# for sentence in all_sentence_lst:
		sentence_lst = sentence.split()
		if root not in sentence_lst:
			return
		root_ind = sentence_lst.index(root)
		root_token = self.nlp(root)[0]
		if root_ind != 0:
			word_in_front_of_root = sentence_lst[root_ind - 1]
			# if it's passive tense
			for item in '''!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~''':
				if item in word_in_front_of_root:
				    word_in_front_of_root = sentence_lst[root_ind - 2]
			if word_in_front_of_root not in dependency_dict: return
			if dependency_dict[word_in_front_of_root][0] == 'auxpass':
				root_aux = word_in_front_of_root
				output += 'How much ' + root_aux + ' '
				for n in dependency_dict:
					if dependency_dict[n][0] == 'nsubjpass':
						if sentence_lst[root_ind-1] in ["has", "had", "have"]:
							theSubj = (" ".join(sentence_lst[:root_ind-1])).split(",")[-1]
						else:
							theSubj = (" ".join(sentence_lst[:root_ind])).split(",")[-1]
				if theSubj == "": return
				# words_before_subj = dependency_dict[theSubj][-1]
				# if len(words_before_subj) != 0:
				# 	output += str(words_before_subj[0]).lower() + ' '
				output += theSubj+ "?"

			else:  # if it's not passive tense
				for n in dependency_dict:
					if dependency_dict[n][0] == 'nsubj':
						if sentence_lst[root_ind-1] in ["has", "had", "have"]:
							theSubj = (" ".join(sentence_lst[:root_ind-1])).split(",")[-1]
						else:
							theSubj = (" ".join(sentence_lst[:root_ind])).split(",")[-1]
				output += 'How much '
				# check tense
				tense = self.parser.check_tense(root, pos_dict)
				if tense != None:
					if tense == "done":
						tense = "did"
					output += tense + ' '
					# check subject
					for n in dependency_dict:
						if dependency_dict[n][0] == 'nsubj':
							if sentence_lst[root_ind-1] in ["has", "had", "have"]:
								theSubj = (" ".join(sentence_lst[:root_ind-1])).split(",")[-1]
							else:
								theSubj = (" ".join(sentence_lst[:root_ind])).split(",")[-1]	
					if theSubj == "": return
					output += theSubj + ' ' + root_token.lemma_ + "?"
				else:
					return None
		return (root,self.parser.check_style(output))

	def howManyQ(self, sentence, ner_tag_dict, dependency_dict, pos_tag_sentence,
				 root):
		Number = ""
		output = ""
		clause = ""
		for k in ner_tag_dict.keys():
			if ner_tag_dict[k] == 'CARDINAL':
				Number = k
		if Number == "": return
		if Number[0].isupper(): return
		if len(Number.split()) > 1: return
		if Number.isnumeric(): return
		sentence_lst = sentence.split()
		if Number not in sentence_lst: return
		if sentence_lst.index(Number) != 0:
			if sentence_lst[sentence_lst.index(Number)-1] == "number": return
		for seg in sentence.replace(';',',').replace(':',',').split(','):
			if Number in seg: clause = seg
		if root not in clause: return
		if " and " in clause: 
			for seg in clause.split('and'):
				if Number in seg: clause = seg
		clause_lst = clause.split()
		if Number not in clause_lst: return
		if root not in clause_lst: return
		root_ind = clause_lst.index(root)
		number_ind = clause_lst.index(Number)
		if number_ind < root_ind:
			output = "How many" + sentence.split(Number, 1)[1][:-1]
		else:
			if root_ind != 0:
				word_in_front_of_root = sentence_lst[root_ind - 1]
				# if it's passive tense
				for item in '''!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~''':
				    if item in word_in_front_of_root:
				        word_in_front_of_root = word_in_front_of_root[:-1]
				if word_in_front_of_root not in dependency_dict: return
				if dependency_dict[word_in_front_of_root][0] == 'auxpass' or dependency_dict[word_in_front_of_root][0] == 'aux':
					middle = clause[clause.find(root): clause.find(Number)]
					middle_lst =  middle.split()
					if dependency_dict[middle_lst[-1]][0] == "amod":
						middle_lst.pop()
						middle_lst.pop()
						middle = " ".join(middle_lst)
					if clause.split(Number, 1)[1][-1] in '''!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~''':
						output = "How many" + clause.split(Number, 1)[1][:-1] + " " + word_in_front_of_root + " " + \
							 clause.split(word_in_front_of_root, 1)[
								 0].lower() + " " + middle
					else:
						output = "How many" + clause.split(Number, 1)[1] + " " + word_in_front_of_root + " " + \
							 clause.split(word_in_front_of_root, 1)[
								 0].lower() + " " + middle
				# if it's not passive tense
				else:
					verb = clause[clause.find(root): clause.find(root) + len(root)]
					if root in self.auxiliary_verbs and sentence_lst[root_ind - 1].lower() == "there":
						if clause.split(Number, 1)[1][-1] in '''!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~''':
							# print(clause.split(Number, 1)[1][:-1])
							# print(clause[clause.find(root): clause.find(Number)])
							output = "How many" + clause.split(Number, 1)[1][:-1] + " " + clause[clause.find(root): clause.find(Number)]
						else:
							# print(clause.split(Number, 1)[1])
							# print(clause[clause.find(root): clause.find(Number)])
							output = "How many" + clause.split(Number, 1)[1] + " " + clause[clause.find(root): clause.find(Number)]
					elif root in self.auxiliary_verbs and sentence_lst[root_ind - 1].lower() != "there":
						middle = clause[clause.find(" "+root+" ")+len(root)+1: clause.find(Number)]
						if clause.split(Number, 1)[1][-1] in '''!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~''':
							# print(clause.split(Number, 1)[1][:-1])
							# print(clause[clause.find(root): clause.find(Number)])
							output = "How many" + clause.split(Number, 1)[1][:-1] + " " + root + " " + clause.split(" "+root+" ", 1)[0] + middle
						else:
							# print(clause.split(Number, 1)[1])
							# print(middle)
							# print(clause.split(root, 1)[0])
							output = "How many" + clause.split(Number, 1)[1] + " " + root + " " + clause.split(" "+root+" ", 1)[0] + middle
					
					# if it's past tense
					elif self.parser.pos_tag_sentence(root)[root][1] in ("VBD", "VBN"):
						if clause.split(Number, 1)[1][-1] in '''!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~''':
							output = "How many" + clause.split(Number, 1)[1][:-1] + " did " + \
									clause.split(Number, 1)[0][0].lower() + \
									clause.split(Number, 1)[0][
									1:clause.find(root)] + self.nlp(verb)[0].lemma_
						else:
							output = "How many" + clause.split(Number, 1)[1] + " did " + \
									clause.split(Number, 1)[0][0].lower() + \
									clause.split(Number, 1)[0][
									1:clause.find(root)] + self.nlp(verb)[0].lemma_
					# if it's not past tense
					else:
						#print(root)
						if clause.split(Number, 1)[1][-1] in '''!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~''':
							output = "How many" + clause.split(Number, 1)[1][:-1] + " does " + \
									clause.split(Number, 1)[0][0].lower() + \
									clause.split(Number, 1)[0][
									1:clause.find(root)] + self.nlp(verb)[0].lemma_
						else:
							output = "How many" + clause.split(Number, 1)[1] + " does " + \
									clause.split(Number, 1)[0][0].lower() + \
									clause.split(Number, 1)[0][
									1:clause.find(root)] + self.nlp(verb)[0].lemma_

		output = ' '.join(output.split()) + "?"
		if output == "?": return
		return self.parser.check_style(output)

	def howLongQ(self, sentence, ner_tag_dict, dependency_dict, pos_tag_sentence,
				  root):
		date = ""
		output = ""
		clause = ""
		sentence = sentence[:-1]
		for k in ner_tag_dict.keys():
			if ner_tag_dict[k] == 'DATE':
				date = k
		if date == "": return
		if date.isnumeric(): return
		if len(date.split()) > 1: return
		date_lst = date.split()
		sentence_lst = sentence.split()
		if root not in sentence_lst: return
		root_lst_ind = sentence_lst.index(root)
		root_ind = sentence.index(root)
		date_ind = sentence.index(date)
		if date_ind < root_ind:
			word_in_front_of_root = sentence_lst[root_lst_ind - 1]
			for item in '''!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~''':
				if item in word_in_front_of_root:
				    word_in_front_of_root = word_in_front_of_root[:-1]
			if word_in_front_of_root not in dependency_dict: return
			if dependency_dict[word_in_front_of_root][0] == 'auxpass':
				sentence_lst[root_lst_ind - 1] = sentence_lst[root_lst_ind - 2]
				sentence_lst[root_lst_ind - 2] = word_in_front_of_root
			else:
				sentence_lst[root_lst_ind] = self.nlp(root)[0].lemma_
				if self.parser.pos_tag_sentence(root)[root][1] in ("VBD", "VBN"):
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
				if word_after_root not in dependency_dict: return
				if dependency_dict[word_after_root][0] != 'prep': word_after_root = ""
				# if it's passive tense
				for item in '''!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~''':
				    if item in word_in_front_of_root:
				        word_in_front_of_root = word_in_front_of_root[:-1]
				if word_in_front_of_root not in dependency_dict: return
				if dependency_dict[word_in_front_of_root][0] == 'auxpass':
					output = "How long " + word_in_front_of_root + " " + \
							 clause.split(word_in_front_of_root, 1)[
								 0].lower() + sentence[root_ind:prep_ind + len(
						word_after_root)]
				else:
					# if it's past tense
					if self.parser.pos_tag_sentence(root)[root][1] in ("VBD", "VBN"):
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
		return self.parser.check_style(output)

	def whyQ(self, sentence, doc, ner_tag_dict, dependency_dict, pos_tag_dict, root):
		# A do sth Because B
		theSubj = ""
		output = ""
		theObj = ""
		sentence_lst = sentence.split()
		if root not in sentence_lst:
			return
		root_ind = sentence_lst.index(root)
		# check tense
		tense = self.parser.check_tense(root, pos_tag_dict)

		if "because" or "due to" or "Due to" in sentence:
			# check if passive tense:
			word_in_front_of_root = sentence_lst[root_ind - 1]
			for item in '''!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~''':
				if item in word_in_front_of_root:
				    word_in_front_of_root = word_in_front_of_root[:-1]
			if word_in_front_of_root not in dependency_dict: return
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
				if tense == None:
					return
				# Get rid of things after because

				# Why + do/does/did sb do sth?
				output += "Why " + tense + " " + theSubj + " " + doc[
					root_ind].lemma_ + " " + theObj + "?"
		return self.parser.check_style(output)

	def whereQ(self, sentence, dep_dict, pos_tags):
		output = ''
		verbs = ['was', 'is', 'were']
		foundVerb = False
		foundVerbInd = 0
		# find tense
		seenWhere = False
		foundWhereInd = 0
		whereInd = 0
		tense = None
		for word in sentence.split():
			if word == 'where':
				seenWhere = True
				foundWhereInd = whereInd
				verb = dep_dict[word][1]
				if verb not in pos_tags: return
				if pos_tags[verb][0] == 'VERB':
					tense = self.parser.check_tense(verb, pos_tags)
				elif verb in verbs:  # if tense is was, is, were
					tense = verb
					foundVerb = True
					foundVerbInd = sentence.split().index(verb)
				break
			whereInd += 1
		if tense == None:  # not able to create question from sentence
			return ""
		output += f'Where {tense} '
		ind = foundWhereInd
		if foundVerb:
			ind = foundVerbInd
		for word in sentence.split()[ind + 1:]:
			output += word + " "
		output = output[:-2] + "?"
		return self.parser.check_style(output)

	# what Question
	def whatQ(self, sentence, dep_dict, root):
		aux_verbs = {"are", "is", "was", "were", "shall", "do", "does", "did",
					 "can", "could", "have", "need", "should", "will", "would",
					 "must", "may", "might", "cannot"}
		output = ''
		if root in aux_verbs:
			output += f"What {root} "
			seenRoot = False
			for n in sentence.split():
				if n == root or n == root + ',':
					seenRoot = True
					continue
				if seenRoot:
					output += n + " "
			return output[:-2] + "?"
		else:
			splitSentence = sentence.split()
			if root in splitSentence:
				rootInd = splitSentence.index(root)
			elif root + ',' in splitSentence:
				rootInd = splitSentence.index(root + ',')
			else:
				return
			if rootInd != 0:
				if splitSentence[rootInd - 1] in aux_verbs:
					output += f'What {splitSentence[rootInd - 1]} {root} '
					output += " ".join(splitSentence[rootInd + 1:])
					return self.parser.check_style(output[:-1] + "?")
				elif rootInd >= 2 and splitSentence[rootInd - 1] == 'be' and \
						splitSentence[rootInd - 2] in aux_verbs:
					output += 'What '
					output += " ".join(splitSentence[rootInd - 2:])
					return self.parser.check_style(output[:-1] + "?")
				else:
					# case where nsubj is before the root
					for word in splitSentence[:rootInd + 1]:
						if word in dep_dict and dep_dict[word][0] == 'nsubj':
							output += 'What '
							output += " ".join(splitSentence[rootInd:])
							return self.parser.check_style(output[:-1] + "?")
			return
	#when question
	def whenQ(self, sentence, ner_tag_dict, root, doc, pos_dict):
		# find DATE/TIME tag
		aux_verbs = {"are", "is", "was", "were", "shall", "do", "does", "did",
					 "can", "could", "have", "need", "should", "will", "would",
					 "must", "may", "might", "cannot"}
		theDateTime = []
		output = ''
		if sentence[-1] == '!' or sentence[-1] == '.':
			sentence = sentence[:-1]
		sentence_lst = sentence.split()
		sentence_lst[0] = sentence_lst[0].lower()
		if sentence_lst[0][-1] == ',': 
			sentence_lst = sentence_lst[1:]
		for k in ner_tag_dict.keys():
			if ner_tag_dict[k] == 'DATE' or ner_tag_dict[k] == 'TIME':
				theDateTime.append(k)
				for elem in theDateTime:
					if elem not in sentence_lst: continue
					index = sentence_lst.index(elem.split()[0])
					if sentence_lst[index-1] == 'on' or sentence_lst[index-1] == 'in':
						sentence_lst = sentence_lst[:index-1] + sentence_lst[index:]
		sentence = " ".join(sentence_lst)
		for ner in theDateTime: 
			sentence = sentence.replace(ner, '')
		sentence_lst = sentence.split()
		if root not in sentence_lst:
			return
		root_ind = sentence_lst.index(root)
		root_token = doc[root_ind]
		if root in aux_verbs:
			output += f"When {root} "
			for n in range(len(sentence_lst)):
				if n == root_ind:
					continue
				else:
					output += sentence_lst[n] + " "
			return self.parser.check_style(output[:-1] + "?")
		else:
			if sentence_lst[root_ind-1] in aux_verbs:
				output += "When " + sentence_lst[root_ind-1] + " "
			if root_ind-2 >=0:
				for n in range(root_ind-2, len(sentence_lst)-1):
					if n == root_ind-1: continue
					output += sentence_lst[n] + " "
			else:
				for n in range(root_ind, len(sentence_lst)-1):
					output += sentence_lst[n] + " "
			return self.parser.check_style(output[:-1] + "?")

