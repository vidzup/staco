from nltk.corpus import wordnet as wn
import pickle
PICKLE_ANTONYMS = 'flantonyms'

def save_antonyms(x):
    pickle.dump(x, open(PICKLE_ANTONYMS,'wb'))

def onetime_get_antonyms():
    owords = dict()
    for i in wn.all_synsets():
        if i.pos() in ['a','s','n']:
            for j in i.lemmas():
                if j.antonyms():
                   owords[j.name()]= j.antonyms()[0].name()
    owords=combine_domain_antonyms(owords)
    save_antonyms(owords)

def load_antonyms():
    opposites = pickle.load(open(PICKLE_ANTONYMS,'r'))
    return opposites

def add_antonyms(w1,w2):
    dt = load_antonyms()
    dt[w1]=w2
    dt[w2]=w1
    save_antonyms(dt)
    return dt 

commonlist=[('get','put'),('Get','Put'),('valid','invalid'),('all','only'),('same','next'),('without','with'),('part', 'full'),('after','before'),('yes','no'),('single','joint'),('local','foreign'),('same','different'),('individual','corporate'),('summary','detail')]

def combine_domain_antonyms(dct):
    for i,j in commonlist:
        dct[i]=j
        dct[j]=i
    return dct
