#!/usr/bin/env python3

import Asking, Parser
import spacy
import sys

class QuestionScorer(object):
    
    # The constructor initializes the language model which is used
    # to analyze the fluency of the questions.
    def __init__(self):
        self.score = 0
        self.bad_start_phrase = [
      'who as ', 'who of ',
      'did no ', 'did although ', 'did however ', 'did see ',
      'did follow ', 'did class ', 'is no ',
      ' who' , ' what ', ' when ', ' how ']
        self.auxiliary_verbs = {"am", "is", "are", "was", "were", "shall", "do",
                            "does", "did","can", "could", "have", "need",
                            "should", "will", "would"}
        self.do_verbs = ["do", "does", "did"]
    
    # Takes a question, as a list of sentence, and returns that question's score
    # only take questions with score > 0
    '''
    do/does/did + am/is/are
    check bracket & quote
    '''
    def score(self, question):
        total_score = 0.1
        #count number of words. If less than 5 than -10.
        lst = question.split(" ")

        #check length
        if len(lst) < 5: 
            total_score -= 1

        #check half parenthesis
        if ("(" in sentence and ")" not in sentence) or (")" in sentence and "(" not in sentence):
            total_score -= 1

        #check double quote
        num_double_quote = 0
        for cur_str in question:
            if cur_str == '"':
                num_double_quote += 1
        if num_double_quote % 2 != 0:
            total_score -= 1

        #check if bad start phrase is in the sentence
        for bad_phrase in self.bad_start_phrase:
            if bad_phrase in self.sentence:
                total_score -= 0.5

        #add score for what and who question
        if question.startswith("What") or question.startswith("Who"):
            total_score += 0.5

        #check do/does/did + am/is/are
        contains_do_verb, contains_aux_verb = False, False
        for verb in self.do_verbs:
            if verb in question:
                contains_do_verb = True
                break
        for verb in self.auxiliary_verbs:
            if verb in self.auxiliary_verbs:
                contains_aux_verb = True
                break
        if (contains_do_verb and contains_aux_verb):
            total_score -= 1

        self.score = total_score

    def check_score(self, score):
        return score > 0














