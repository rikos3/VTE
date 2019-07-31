
from os.path import expanduser
HOME = expanduser("~")
MMI = HOME + "/multimodal_inference"
C2L = HOME + "/ccg2lambda"

import sys
sys.path.append(C2L + "/scripts")

from linguistic_tools import *
from nltk.sem.logic import *
import pickle

lexpr = Expression.fromstring

# load 2-place predicates
with open(MMI + '/data/two_predicates.pkl', 'rb') as f:
    two_predicates = pickle.load(f)

def addAxiom(g_preds, words_elst):
  avoid_lst = []
  assumptions = []
  for g_pred in g_preds:
    g = str(g_pred)
    if not g in two_predicates:
      all_x = "x"
      x = "(x)"
      synonyms = wn.synsets(g)
      for word in words_elst.keys():
        synonyms_lemma = [lemma for synonym in synonyms if (synonym.name() == word) \
                          for lemma in synonym.lemma_names() if (not lemma in two_predicates and lemma != g)]
        hyper = lambda s: s.hypernyms()
        hypernyms_lemma = [lemma for synonym in synonyms \
                           for hypernym in synonym.closure(hyper) if (hypernym.name() == word) \
                           for lemma in hypernym.lemma_names() if (not lemma in two_predicates)]
        hyponyms_lemma = [lemma for synonym in synonyms \
                          for hyponym in synonym.hyponyms() if (hyponym.name() == word) \
                          for lemma in hyponym.lemma_names() if (not lemma in two_predicates)]
        antonyms_lemma = [lemma for synonym in synonyms \
                          for antonym in synonym.lemmas()[0].antonyms() \
                          if (antonym.synset().lemmas()[0].synset().name() == word) \
                          for lemma in antonym.synset().lemma_names() \
                          if (not lemma in two_predicates)]
        for f in synonyms_lemma:
          f = f.replace('-','_')
          assumptions.append(lexpr('all ' + all_x + '.(' + f + x + ' <-> ' + g + x + ')'))
          avoid_lst.append(g_pred)
        for f in hypernyms_lemma:
          f = f.replace('-','_')
          assumptions.append(lexpr('all ' + all_x + '.(' + g + x + ' -> ' + f + x + ')'))
        for f in hyponyms_lemma:
          f = f.replace('-','_')
          assumptions.append(lexpr('all ' + all_x + '.(' + f + x + ' -> ' + g + x + ')'))
          avoid_lst.append(g_pred)
        for f in antonyms_lemma:
          f = f.replace('-','_')
          assumptions.append(lexpr('all ' + all_x + '.(' + f + x + ' -> -' + g + x + ')'))
  return(assumptions, avoid_lst)

def addAxiom2(g_preds, words_elst):
  avoid_lst = []
  assumptions = []
  for g_pred in g_preds:
    g = str(g_pred)
    if not g in two_predicates:
      all_x = "x"
      x = "(x)"
      synonyms = [word for word in obtain_synonyms(g) if (word in list(words_elst.keys()) and word != g)]
      hypernyms = [word for word in obtain_hypernyms(g) if (word in list(words_elst.keys()) and word != g)]
      hyponyms = [word for word in obtain_hyponyms(g) if (word in list(words_elst.keys()) and word != g)]
      antonyms = [word for word in obtain_antonyms(g) if (word in list(words_elst.keys()) and word != g)]
      for f in synonyms:
        fn = f.replace('-','_')
        assumptions.append(lexpr('all ' + all_x + '.(' + f + x + ' <-> ' + g + x + ')'))
        avoid_lst.append(g_pred)
      for f in hypernyms:
        f = f.replace('-','_')
        assumptions.append(lexpr('all ' + all_x + '.(' + g + x + ' -> ' + f + x + ')'))
      for f in hyponyms:
        f = f.replace('-','_')
        assumptions.append(lexpr('all ' + all_x + '.(' + f + x + ' -> ' + g + x + ')'))
        avoid_lst.append(g_pred)
      for f in antonyms:
        f = f.replace('-','_')
        assumptions.append(lexpr('all ' + all_x + '.(' + f + x + ' -> -' + g + x + ')'))
  return(assumptions, avoid_lst)
