#!/usr/bin/env python3 -W ignore::DeprecationWarning
# -*- coding:utf8 -*-
import nltk
from nltk.tokenize import sent_tokenize
import spacy
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from nltk.corpus import wordnet, stopwords
# import pattern3
# from pattern.en import conjugate, lemma, lexeme,PRESENT,SG
import en_core_web_sm
import Parser
from sentence_transformers import SentenceTransformer #BERT sentence embeddings


# # Question Answering

# ## Tools to Use

class Answering(object):
    def __init__(self, textFile):
        self.nlp = en_core_web_sm.load()
        self.auxiliary_verbs = ["am", "is", "are", "was", "were", "shall", "do",
                                "does", "did","can", "could", "have", "need",
                                "should", "will", "would"]
        self.question_types = ["Who", "When", "What" , "Where"," How many", "How long", "How much", "Why"]
        self.parser = Parser.Parser(textFile)
        self.text = self.parser.text
        self.sbert_model = SentenceTransformer('bert-base-nli-mean-tokens')
        self.sw_nltk = stopwords.words('english')
        self.sentence_emb_text = self.sentence_emb(self.text)

    #input: text file 
    #output: a dictionary of sentence embeddings {sentence: sentence embeddings}
    def sentence_emb(self,text):
        result = dict()
        for sentence in text:
            sentence_emb = np.array(self.sbert_model.encode(sentence)).reshape(1, -1)
            result[sentence] = sentence_emb
        return result

    #input: question, text embedding dict
    def find_best_sentence(self, question):
        question_emb = np.array(self.sbert_model.encode(question)).reshape(1, -1)
        sim_max = 0
        output = ""
        for sentence, sentence_emb in self.sentence_emb_text.items():
            sim = cosine_similarity(sentence_emb, question_emb)
            if sim > sim_max:
                sim_max = sim
                output = sentence
        return output, sim_max


    def check_question_type(self, question):
        #Check Question type
        for q_type in self.question_types:
            if question.startswith(q_type):
                return q_type
        for a_verb in self.auxiliary_verbs:
            a_verb = a_verb[0].upper() + a_verb[1:]
            if question.startswith(a_verb):
                return a_verb
        return "No idea"


    #find sentence with question type as an argument
    def find_best_k_sentence(self, question, k):
        question_type = self.check_question_type(question)
        question_emb = np.array(self.sbert_model.encode(question)).reshape(1, -1)
        sims_dict = dict()
        output = ""
        for sentence, sentence_emb in self.sentence_emb_text.items():
            sim = cosine_similarity(sentence_emb, question_emb)
            #if question type and NER matches, +1
            if self.check_NER(sentence, question_type):
                sim += 1
            #check extra matching bonus
            extra = self.NER_match(question, sentence)
            # print(extra, sentence)
            sims_dict[sentence] = sim + extra
        sorted_sim = sorted(sims_dict.items(), key = lambda kv: kv[1])[::-1][:k]
        return sorted_sim



    #find same NER keys 
    #find same words after getting rid of stopwords
    def NER_match(self, question, sentence):
        output = 0
        question_ner = self.parser.ner_tag_sentence(question)
        sentence_ner = self.parser.ner_tag_sentence(sentence)
        #find same NER key and add 0.2 for each
        for key in question_ner.keys():
            # print(key)
            all_keys = [key.lower() for key in sentence_ner.keys()]
            if key.lower() in all_keys:
                output += 0.2
        #find same words and plus 0.1 for each
        q_words = [word for word in question.split() if word.lower() not in self.sw_nltk]
        s_words = [word for word in sentence.split() if word.lower() not in self.sw_nltk]
        for word in q_words:
            if word in s_words:
                output += 0.1
        return output


    #check if the sentence contains certain NER tags
    #When - DATE
    #Who - PERSON
    #Where" - FAC, ORG, ORG, ORG
    #"How many" - CARDINAL
    #"How long" - DATE
    #"How much" - MONEY
    #"Why" - "because"

    def check_NER(self, sentence, question_type):
        output = False
        ner_tag_dict = self.parser.ner_tag_sentence(sentence)
        if question_type == "When":
            if ("TIME" in ner_tag_dict.values()) or ("DATE" in ner_tag_dict.values()):
                output = True
        elif question_type == "Who":
            if ("PERSON" in ner_tag_dict.values()):
                output = True
        elif question_type == "Where":  
            if ("FAC" in ner_tag_dict.values()) or ("ORG" in ner_tag_dict.values()) or ("ORG" in ner_tag_dict.values()) or ("LOC" in ner_tag_dict.values()):
                output = True
        elif question_type == "How much":
            if ("MONEY" in ner_tag_dict.values()):
                output = True
        elif question_type == "How long":
            if ("DATE" in ner_tag_dict.values()):
                output = True
        elif question_type == "How many":
            if ("CARDINAL" in ner_tag_dict.values()):
                output = True
        elif question_type == "How often":
            if ("CARDINAL" in ner_tag_dict.values()):
                output = True
        elif question_type == "Why":
            if ("because" in sentence) or ("due to" in sentence) or ("Due to" in sentence):
                output = True
        else:
            for aux in self.auxiliary_verbs:
                aux_cap = aux[0].upper() + aux[1:]
                if aux or aux_cap in sentence:
                    output = True
        return output


    #Binary Questions
    #Strip the punctuation at the end
    #input: question and original sentence in text
    #check : 1) negation words: no/not/'nt √ 
    #        2) Adjectives -> check antonymn
    #        3) Check Info matching?

    def binary_answer(self, question):
        negate = False
        output = ""
        neg_words = {'no', 'not', "don't", "doesn't", "did't", "haven't", "hasn't", "wasn't", "weren't"}
        sentence = self.find_best_k_sentence(question, 1)[0][0]
        sentence_set = set([x.lower() for x in sentence.split()])
        question_set = set([x.lower() for x in question[:-1].split()])
        intersect_words = sentence_set.intersection(question_set)
        leftover_question = question_set - intersect_words
        leftover_sentence = sentence_set - intersect_words
        # print("leftover words: ")
        # print(leftover_question, leftover_question)
        
        negate = not self.check_negate(leftover_question, leftover_question)
        if negate:
            #No
            output += "No. " + sentence
        else:
            #Yes
            output += "Yes. " + sentence

        return output


    #neg_words = ['no', 'not',"n't"]
    #return true if same
    def check_negate(self, set1, set2):
        # print("hi")
        negate1, negate2 = True, True
        # print("Negate", negate1, negate2)
        if len(set1) == 0 and len(set2) == 0:
            return negate1 and negate2
        for item1 in set1:
            if (item1 == 'no') or (item1 == 'not') or ("n't" in item1):
                negate1 = not negate1
                # print("1", item1)

        for item2 in set2:
            if (item2 == 'no') or (item2 == 'not') or ("n't" in item2):
                negate2 = not negate2
                # print("2", item2)
        # print("Negate", negate1 and negate2)
                
        return negate1 and negate2 


    # # Get Answer

    def get_answer_from_text(self, question):
        k = 1
        best_k_sentence = self.find_best_k_sentence(question, k)
        top_sentence = best_k_sentence[0]
        return top_sentence[0]



    def relativeWhoClause(self, answer, question):
        ner_dict = self.parser.ner_tag_sentence(self.nlp(answer.split(",")[0]+','))
        if ner_dict == {}: return answer
        output = list(ner_dict.keys())[-1]
        if ner_dict[output] not in ["PERSON"]:
            return answer
        else:
            question = question[:-1]
            question_list = question.split(" ")
            question_list.pop(0)
            question_list.insert(0,output)
            return " ".join(question_list) + "."


    def relativeWhenClause(self, answer, question):
        ner_dict = self.parser.ner_tag_sentence(self.nlp(answer.split(",")[0]+','))
        if ner_dict == {}: return answer
        output = list(ner_dict.keys())[-1]
        if ner_dict[output] not in ["DATE", "TIME"]: return answer
        else:
            question_list = question.split(" ")
            if question_list[1] in ["is", "are", "was", "were"]:
                curr = question_list[1]
                root = self.parser.dependency_dict(self.nlp(question))[1]
                if root in ["is", "are", "was", "were"]: return answer
                question = question[:-1]
                question_list = question.split(" ")
                root_index = question_list.index(root)
                question_list.insert(root_index, curr)
                question_list.pop(0)
                question_list.pop(0)
                return " ".join(question_list) + " at " + output + "."
            elif question_list[1] in ["do", "does", "did"]:
                if question_list[1] == "does":
                    root = self.parser.dependency_dict(self.nlp(question))[1]
                    root_index = question_list.index(root)
                    # new_root = lexeme(root)[1]
                    new_root = root
                    question_list[root_index] = new_root
                    question_list.pop(0)
                    question_list.pop(0)
                    return " ".join(question_list) + " at " + output + "."
                elif question_list[1] == "do":
                    question_list.pop(0)
                    question_list.pop(0)
                    return " ".join(question_list) + " at " + output + "."
                else:
                    root = self.parser.dependency_dict(self.nlp(question))[1]
                    root_index = question_list.index(root)
                    # new_root = lexeme(root)[3]
                    new_root = root
                    question_list[root_index] = new_root
                    question_list.pop(0)
                    question_list.pop(0)
                    return " ".join(question_list) + " at " + output + "."
            else:
                return answer


    def relativeWhereClause(self, answer, question):
        ner_dict = self.parser.ner_tag_sentence(self.nlp(answer.split(",")[0]+','))
        output = list(ner_dict.keys())[-1]
        if ner_dict[output] not in ["FAC", "ORG", "GPE", "LOC"]:
            return answer
        else:
            question = question[:-1]
            question_list = question.split(" ")
            if question_list[1] in ["is", "are", "was", "were"]:
                curr = question_list[1]
                root = self.parser.dependency_dict(self.nlp(question))[1]
                root_index = question_list.index(root)
                question_list.insert(root_index, curr)
                question_list.pop(0)
                question_list.pop(0)
                return " ".join(question_list) + " at " + output + "."
            elif question_list[1] in ["do", "does", "did"]:
                if question_list[1] == "does":
                    root = self.parser.dependency_dict(self.nlp(question))[1]
                    root_index = question_list.index(root)
                    #new_root = lexeme(root)[1]
                    new_root = root
                    question_list[root_index] = new_root
                    question_list.pop(0)
                    question_list.pop(0)
                    return " ".join(question_list) + " at " + output + "."
                elif question_list[1] == "do":
                    question_list.pop(0)
                    question_list.pop(0)
                    return " ".join(question_list) + " at " + output + "."
                else:
                    root = self.parser.dependency_dict(self.nlp(question))[1]
                    root_index = question_list.index(root)
                    #new_root = lexeme(root)[3]
                    new_root = root
                    question_list[root_index] = new_root
                    question_list.pop(0)
                    question_list.pop(0)
                    return " ".join(question_list) + " at " + output + "."
            else:
                return answer


    def get_answer(self, answer, question):
        question_emb = np.array(self.sbert_model.encode(question)).reshape(1, -1)
        answer_emb = np.array(self.sbert_model.encode(answer)).reshape(1, -1)
        overall_sim = cosine_similarity(answer_emb, question_emb)
        max_sim = 0
        max_part = None
        for sentence in answer.split(','):
    #         print(sentence)
            if sentence.startswith(' '): 
                sentence = sentence[1:]
    #         print(sentence)
            sentence_emb = np.array(self.sbert_model.encode(sentence)).reshape(1, -1)
            curr_sim = cosine_similarity(sentence_emb, question_emb)
    #         print(curr_sim)
            if curr_sim > max_sim and self.check_complete_sentence(sentence):
                max_sim = curr_sim
                max_part = sentence
        if max_part == None or overall_sim > max_sim:
            max_part = answer
        if max_part[-1] != '.':
            max_part += '.'
        if max_part.startswith("who"):
            max_part = self.relativeWhoClause(answer, question)
        elif max_part.startswith("where"):
            max_part = self.relativeWhereClause(answer, question)
        elif max_part.startswith("when"):
            max_part = self.relativeWhenClause(answer, question)
        return max_part[0].upper() + max_part[1:]



    def check_complete_sentence(self, sentence):
        complete = False
        dependence_dict, root = self.parser.dependency_dict(self.nlp(sentence))
    #     print(dependence_dict)
        for item in dependence_dict.values():
            if (item[0] == 'nsubj' or item[0] == 'nsubjpass'):
                complete = True
        return complete

    def check_binary_question(self, question):
        start = question.split(" ")[0]
        return start.lower() in self.auxiliary_verbs


# gAnswer = GenerateAnswers("data/set4/a7.txt")


# ## Test case:

# # Binary
# question1 = "Is Harry Potter and the Prisoner of Azkaban a a 2004 fantasy film directed by Alfonso Cuarón and distributed by Warner Bros?"
# answer1 = gAnswer.binary_answer(question1)
# print(answer1)
# print(gAnswer.get_answer(answer1, question1))

# # In[41]:


# # Who
# question2 = "Who has been spending another unhappy summer at Privet Drive?"
# answer2 = gAnswer.get_answer_from_text(question2)
# print(answer2)
# print(gAnswer.get_answer(answer2, question2))


# # In[42]:


# # When
# question3 = "When was the film released in United Kingdom?"
# answer3 = gAnswer.get_answer_from_text(question3)
# print(answer3)
# print(gAnswer.get_answer(answer3, question3))


# # In[43]:


# # What
# question4 = "What is found ruined and empty?"
# answer4 = gAnswer.get_answer_from_text(question4)
# print(answer4)
# print(gAnswer.get_answer(answer4, question4))


# # In[44]:


# # Where
# question5 = "Where is Harry forgiven by Minister of Magic Cornelius Fudge for using magic outside of Hogwarts?"
# answer5 = gAnswer.get_answer_from_text(question5)
# print(answer5)
# print(gAnswer.get_answer(answer5, question5))


# # In[45]:


# # Where
# question5 = "Where was the film released on 31 May 2004?"
# answer5 = gAnswer.get_answer_from_text(question5)
# print(answer5)
# print(gAnswer.get_answer(answer5, question5))


# # In[46]:


# # Why
# question6 = "Why did Oldman accept the part?"
# answer6 = gAnswer.get_answer_from_text(question6)
# print(answer6)
# print(gAnswer.get_answer(answer6, question6))


# # In[47]:


# # How much
# question7 = "How much did the Prisoner of Azkaban grossed a total of worldwide?"
# answer7 = gAnswer.get_answer_from_text(question7)
# print(answer7)
# print(gAnswer.get_answer(answer7, question7))


# # In[48]:


# # How many
# question8 = "How many Academy Awards was the film nominated for?"
# answer8 = gAnswer.get_answer_from_text(question8)
# print(answer8)
# print(gAnswer.get_answer(answer8, question8))


# # In[49]:


# # How long
# question9 = "How long after Harris's death, did Cuaron choose Gambon as his replacement?"
# answer9 = gAnswer.get_answer_from_text(question9)
# print(answer9)
# print(gAnswer.get_answer(answer9, question9))





