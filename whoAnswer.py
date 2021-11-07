def whoAnswer(question, sentence, dependency_dict):
    first_word = question.split()[0]
    if first_word == 'Who':
        theName = ''
        ner_tag_s1 = ner_tag_sentence(s1)
        for k in ner_tag_s1.keys():
            names = k.split()
            for n in names:
                if dependency_dict[n][0] == 'nsubj':
                    theName = k
    return theName


def whenAnswer(question, sentence):
    first_word = question.split()[0]
    if first_word == 'When':
        theDateTime = ''
        ner_tag_s1 = ner_tag_sentence(sentence)
        for k in ner_tag_s1.keys():
            if ner_tag_s1[k] == 'DATE' or ner_tag_s1[k] == 'TIME':
                theDateTime = k
    return theDateTime