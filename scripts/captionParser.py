# coding: utf-8


with open("../vte_location.txt", "r") as f:
	VTE = f.read().rstrip("\n")
with open("../ccg2lambda_location.txt", "r") as f:
	C2L = f.read().rstrip("\n")

import pickle
import json
import subprocess
import argparse
from itertools import groupby
from operator import itemgetter

from nltk.sem import Valuation, Model
from nltk.sem.logic import * 
from nltk.stem import WordNetLemmatizer

import sys
sys.path.append(VTE + "/scripts")
sys.path.append(C2L + "/scripts")

import time
def progress(i, l):
  sys.stdout.write("\r[ {} / {}]".format(i, l))
  sys.stdout.flush()

import make_compound as mcomp
from linguistic_tools import *
from add_axiom import addAxiom
from read_xml import use_lesk

with open(VTE + "/data/grim.json", "r") as f:
  grim_lst = json.load(f)

lemmatizer = WordNetLemmatizer()
lexpr = Expression.fromstring

def get_atomic_formulas2(expression):
  if isinstance(expression, ApplicationExpression):
    return set([expression])
  elif isinstance(expression, EqualityExpression):
    return set([expression])
  elif isinstance(expression, IndividualVariableExpression):
    return set([expression])
  elif isinstance(expression, EventVariableExpression):
    return set([expression])
  elif isinstance(expression, FunctionVariableExpression):
    return set([expression])
  elif isinstance(expression, ConstantExpression):
    return set([expression])
  elif isinstance(expression, NegatedExpression):
    return set([expression])
  elif isinstance(expression, OrExpression):
    return set([expression])
  elif isinstance(expression, ImpExpression):
    return set([expression])
  elif isinstance(expression, AllExpression):
    return set([expression])
  else:
    return expression.visit(get_atomic_formulas2,
            lambda parts: reduce(operator.or_, parts, set()))

# Input: pred=man, arg=x01, wn_data={man: (man.n.01, 'n')}, words_elst={man.n.01: [(d1,)]}
# Output: {x01: [(d1,)]}
def check_wn_data(pred, arg, wn_data, words_elst, arg_elst):
  wn_pred = wn_data[pred][0] if wn_data.get(pred) is not None else None
  e_lst = words_elst.get(wn_pred.name(), []) if wn_pred is not None else []
  if e_lst != [] and e_lst is not None:
    arg_elst[arg] = e_lst
    success = True
  else:
    success = False
  return(success, arg_elst)

# Input: pred=man, arg=x01, valuations{man: [(d1,)]}
# Output: {x01: [(d1,)]}
def check_valuation(pred, arg, valuations, arg_elst):
  e_lst = arg_elst.get(arg, [])
  val_lst = list(valuations.get(pred, set()))
  e_lst.extend(val_lst)
  e_lst = [e for e in list(set(e_lst)) if len(e) == 1]
  if e_lst != [] and e_lst is not None:
    arg_elst[arg] = e_lst
    success = True
  else:
    success = False
  return(success, arg_elst)

def check_synsets(pred, arg, synsets, wn_data, words_elst, arg_elst):
  e_lst = arg_elst.get(arg, [])
  for word in synsets:
    wn_pred = wn_data.get(word, [None])[0]
    e_lst.extend(words_elst.get(wn_pred, []))
  e_lst = [e for e in list(set(e_lst)) if len(e) == 1]
  if e_lst != [] and e_lst is not None:
    arg_elst[arg] = e_lst
  return(arg_elst)

# Check whether arg1 and arg2 correspond each entity.
def check_elst(arg1, arg2, arg_elst):
  e_lst1 = arg_elst.get(arg1, [])
  e_lst2 = arg_elst.get(arg2, [])
  success = True if ( e_lst1 != [] and e_lst2 != [] ) else False
  return(success, e_lst1, e_lst2)

# Get the pair of entities if there is a synonym or a hyponym of a target predicate in WordNet.
def get_plst(pred, p_lst, wn_data, words_elst, valuations):
  for two_pred in two_predicates:
    # pred(cover) <-> two_pred(occlude) or pred(play) -> two_pred(touch)
    wn_pred = wn_data.get(two_pred, [None])[0]
    if ( is_synonym(pred, two_pred) or is_hyponym(pred, two_pred) ):
      p_lst.extend(words_elst.get(wn_pred, []))
      p_lst.extend(list(valuations.get(two_pred, set())))

  if pred in ['sit_in', 'sit_on', 'lie_on', 'lie_in', 'wear']:
    two_pred = 'touch'
    wn_pred = wn_data.get(two_pred, [None])[0]
    p_lst.extend(words_elst.get(wn_pred, []))
    p_lst.extend(list(valuations.get(two_pred, set())))

  if pred in ['in_front_of']:
    two_pred = 'near'
    wn_pred = wn_data.get(two_pred, [None])[0]
    p_lst.extend(words_elst.get(wn_pred, []))
    p_lst.extend(list(valuations.get(two_pred, set())))

  p_lst = list(set(p_lst))
  return(p_lst)

# Get a new entity which is not included in FOL structure.
def get_newEntity(domain):
  i = 1
  new_entity = 'dd' + str(i)
  while {new_entity}.issubset(domain):
    i += 1
    new_entity = 'dd' + str(i)
  return(new_entity)

def make_noteq(lst, arg_elst, domains):
  expr1 = lst[0]
  arg1 = expr1.term.first
  e_lst1 = arg_elst.get(arg1, [])
  lst2 = []
  noteqs = []
  for expr in lst:
    if expr.term.first == arg1:
      lst2.append(expr)
      noteqs.append(expr.term.first)
      noteqs.append(expr.term.second)
    elif expr.term.second == arg1:
      lst2.append(expr)
      noteqs.append(expr.term.first)
      noteqs.append(expr.term.second)
    else:
      pass
  noteqs = list(set(noteqs))
  while True:
    if len(e_lst1) < len(noteqs):
      new_entity = get_newEntity(domains)
      domains.add(new_entity)
      e_lst1.append((new_entity,))
    else:
      break
  return(arg_elst, domains)


def caption_parser(key):

  #print('Key: ' + key)

  domains = model[key].domain
  valuations = model[key].valuation
  predicates = valuations.keys()
  comments = []
  errors = []
  words_elst = words_elsts[key]

  hypo_data = {}
  for model_pred in predicates:
    hyponyms = obtain_hyponyms(model_pred)
    for hypo in hyponyms:
      hyponyms.union(obtain_hyponyms(hypo))
    hypo_data[model_pred] = list(hyponyms)

  #Parse captions
  output = subprocess.run([VTE + "/scripts/parse_multi_caption.sh", parser, key], \
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  texts = output.stdout.decode('utf-8')
  text_lst = [text for text in texts.split("\n") if text != '']

  xmlfile = VTE + "/work/captions/" + key + "." + parser + ".sem.xml"
  wn_data_lst = use_lesk(xmlfile)

  tokfile = VTE + '/work/captions/' + key + ".tok.w2n"
  with open(tokfile) as f:
    lines = f.readlines()
  
  for i in range(len(text_lst)):
    text = text_lst[i].strip()
    #print('Input: ' + lines[i].strip())

    # wn_data --> key: man value: (man.n.01, n)
    wn_data = wn_data_lst[i]
   
    try:
      lexpr(text)
      success = True
    except:
      success = False

    if success:
      expr = lexpr(mcomp.make_compound(text))
     #print('FOL: ' + str(expr))

      if isinstance(expr, AllExpression):
        term = expr.term
        success = False
        comments.append(expr)
      else:
        success = True

    if success:
      expr_lst = get_atomic_formulas2(expr)
      arg_elst = {}
      pred_1 = []
      pred_av = []
      pred_2 = []
      preds = []
      pass_lst = []
      eq_expr_lst = []
      noteq_expr_lst = []
      negapp_expr_lst = []
      fun_lst = []

      for expr in expr_lst:
        f, args = mcomp.split_app(expr, [])
        pred = str(f)
        lemmatized_pred = lemmatizer.lemmatize(pred)
        fun_lst.append(pred)

        # 1-place predicate
        len_args = len(args)
        if len_args == 1:
          arg = args[0]
          pred_1.append((pred, arg))

          pos = wn_data.get(pred, [None,None])[1]
          lem_pos = wn_data.get(lemmatized_pred, [None,None])[1]

          if (pos == 'n' or lem_pos == 'n'):
            is_n = True
          else:
            is_n = False

          if is_n:
            preds.append(pred)

            success_wn, arg_elst = check_wn_data(lemmatized_pred, arg, wn_data, words_elst, arg_elst)
  
            if not success_wn:
  
              success_val1, arg_elst = check_valuation(lemmatized_pred, arg, valuations, arg_elst)
              success_val2, arg_elst = check_valuation(pred, arg, valuations, arg_elst)
              success_val = success_val1 or success_val2
              
              if not success_val:
                synonyms = obtain_synonyms(lemmatized_pred)
                arg_elst = check_synsets(lemmatized_pred, arg, synonyms, wn_data, words_elst, arg_elst)

                synonyms = obtain_synonyms(pred)
                arg_elst = check_synsets(pred, arg, synonyms, wn_data, words_elst, arg_elst)

                for model_pred in predicates:
                  hyponyms = hypo_data.get(model_pred, [])
                  if pred in hyponyms:
                    e_lst = list(valuations.get(model_pred, []))
                    if len(e_lst[0]) == len_args:
                      arg_elst[arg] = e_lst
  
              if arg_elst.get(arg) is None:
                pass_lst.append((pred, arg))

          else:
            pred_av.append(pred)
         
        # 2-place predicate
        elif len_args == 2:
          pred_2.append((pred, args))

        else:
          if isinstance(expr, EqualityExpression):
            eq_expr_lst.append(expr)

          elif isinstance(expr, NegatedExpression):
            if isinstance(expr.term, EqualityExpression):
              noteq_expr_lst.append(expr)
            elif isinstance(expr.term, ApplicationExpression):
              negapp_expr_lst.append(expr)

      # for (x=y)
      for expr in eq_expr_lst:
        arg1 = expr.first
        arg2 = expr.second
        e_lst1 = arg_elst.get(arg1, [])
        e_lst2 = arg_elst.get(arg2, [])
        e_lst1.extend(e_lst2)
        e_lst = list(set(e_lst1))
        
        arg_elst[arg1] = e_lst
        arg_elst[arg2] = e_lst

      # for -(x=y)
      if noteq_expr_lst != []:
        arg_elst, domains = make_noteq(noteq_expr_lst, arg_elst, domains)

      # for -(F(x))
      for expr in negapp_expr_lst:
        f, args = mcomp.split_app(expr.term, [])
        pred = str(f)
        valuations[pred] = set()
        preds.append(pred)

      for pred, arg in pass_lst:
        e_lst = arg_elst.get(arg, [])
        if e_lst is None:
          new_entity = get_newEntity(domains)
          domains.add(new_entity)
          arg_elst[arg] = [(new_entity,)]

      for pred, g in groupby(sorted(pred_1), key=itemgetter(0)):
        preds.append(pred)
        e_set = valuations.get(pred, set())
        for pred1, arg1 in g:
          e_set1 = set(arg_elst.get(arg1, []))
          e_set.union(e_set1)

        if pred in pred_av:
          if len(list(e_set)) == 1:
            valuations[pred] = e_set
        else:
          if len(list(e_set)) != 0:
            valuations[pred] = e_set

      preds = list(set(preds))

      #for pred in preds:
      #  e_set = valuations.get(pred)
      #  if e_set is not None:
      #    print(' * ', pred + '(' +  str(arg1) + ')', list(e_set))

      # 2-place predicate
      for pred, args in pred_2:
        arg1 = args[0]
        arg2 = args[1]
        e_lst = []
        p_lst = []
        
        if pred in two_predicates:
          p_lst0 = words_elst.get(pred, [])

        else:
          p_lst0 = []

        wn_pred = wn_data[pred][0].name() if (wn_data.get(pred) is not None and wn_data.get(pred)[0] is not None) else None
        
        if wn_pred is not None:
          p_lst = get_plst(wn_pred, p_lst, wn_data, words_elst, valuations)

        if p_lst == []:
          p_lst = get_plst(pred, p_lst, wn_data, words_elst, valuations)

        success_elst, e_lst1, e_lst2 = check_elst(arg1, arg2, arg_elst)

        if success_elst:
          if ( len(e_lst1) == 1 and len(e_lst2) == 1 ):
            e_lst.append((list(e_lst1)[0][0],list(e_lst2)[0][0]))
          else:
            for e1 in e_lst1:
              for e2 in e_lst2:
                if (e1[0], e2[0]) in p_lst:
                  e_lst.append((e1[0],e2[0]))

        e_lst.extend(p_lst0)
        e_lst = list(set(e_lst))

        #if e_lst != []:
        #  valuations[pred] = set(e_lst)
        #  print(' * ', pred + '(' + str(arg1) + ',' + str(arg2) + ')', e_lst)
        #else:
        #  pass

    else:
      errors.append((text, output))

  return(valuations, comments, errors)


if __name__ == '__main__':

  parser0 = argparse.ArgumentParser()
  parser0.add_argument("--input", default='structure', help='File name of structure data (default=structure)')
  parser0.add_argument("--output", default='structure_cap', help='File name of structure data extended by captions (default=structure_cap)')
  parser0.add_argument("--parser", default='candc', help='Choose candc, easyccg or depccg as a parser (default=candc)')
  args = parser0.parse_args()

  # load model
  with open(VTE + '/work/' + args.input + '.pkl', 'rb') as f:
    model = pickle.load(f)

  # load words_elst
  with open(VTE + '/work/words_elst.pkl', 'rb') as f:
    words_elsts = pickle.load(f)

  # load two_predicates
  with open(VTE + '/data/two_predicates.pkl', 'rb') as f:
    two_predicates = pickle.load(f)

  parser = args.parser

  keys = model.keys()
  new_model = {}
  comments_data = {}
  parse_error = {}

  # construct a new Model.
  for i, key in enumerate(keys):
    progress(i, len(keys))
    new_val, comments, errors = caption_parser(key)
    dom = new_val.domain
    m = Model(dom, new_val)
    new_model[key] = m
    comments_data[key] = comments
    parse_error[key] = errors

  progress(len(keys), len(keys))
  sys.stdout.write("\nfinish!\n")

  # save
  with open(VTE + '/work/' + args.output + '.pkl', 'wb') as f:
    pickle.dump(new_model, f, protocol=2)

  # save
  with open(VTE + '/work/comments.pkl', 'wb') as f:
    pickle.dump(comments_data, f, protocol=2)

  # save
  with open(VTE + '/work/parse_errors.pkl', 'wb') as f:
    pickle.dump(parse_error, f, protocol=2)
