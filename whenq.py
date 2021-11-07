def check_tense(root_ind, pos_dict):
    tag = pos_dict[root_ind][0][2]
    if tag == "VB":
        return "do"
    elif tag == "VBD":
        return "did"
    elif tag == "VBG":
        return "doing"
    elif tag ==  "VBN":
        return "done"
    elif tag == "VBP":
        return "do"
    elif tag == "VBZ":
        return "does"
    else:
        return None

import re
def whenQ(sentence, ner_tag_dict, dependency_dict, root, doc, pos_dict):
    #find DATE/TIME tag
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
        tense = check_tense(root_ind, pos_dict)
        output+= tense + ' ' + sentence
    else:
        sentence = sentence.replace(theDateTime, '')
        sentence = sentence.replace(aux, '')
        output = 'When ' + aux + ' '+ sentence
        output = output.lower()
    output = output[0].upper() + output[1:]
    output = output.split(" ")
    output = " ".join(output)
    output = output[0:len(output)-1] + "?"
    return output