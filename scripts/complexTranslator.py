# coding: utf-8

from os.path import expanduser
HOME = expanduser("~")

MMI = HOME + "/Multimodal_Inference"

import pickle
import argparse
from nltk.sem.logic import *

lexpr = Expression.fromstring

def eq(e_lst):
  txts = []
  l = len(e_lst)
  for i in range(l-1):
    for j in range(i+1, l):
      txts.append("(" + e_lst[i] + " = " + e_lst[j] + ")")
  return(txts)

def noteq(e_lst):
  txts = []
  l = len(e_lst)
  for i in range(l-1):
    for j in range(i+1, l):
      txts.append("-(" + e_lst[i] + " = " + e_lst[j] + ")")
  return(txts)

def forall1(pred, e_lst):
  txt = ""
  for e in e_lst[:-1]:
    e = e[0]
    txt += "(x = " + e + ") | "
  e = e_lst[-1][0]
  txt += "(x = " + e +")"
  txt = "all x.(" + pred + "_1(x) <-> " + txt + ")"
  return(txt)

def forall2(pred, e_lst):
  txt = ""
  for e1, e2 in e_lst[:-1]:
    txt += "(x = " + e1 + " & y = " + e2 + ") | "
  e1, e2 = e_lst[-1]
  txt += "(x = " + e1 + " & y = " + e2 + ")"
  txt = "all x y.(" + pred + "(x,y) <-> " + txt + ")"
  return(txt)

def forall(dom, vals):
  txts = []
  preds = vals.keys()
  preds = list(set(preds) - set("entity"))
  d_lst = sorted(list(dom))
  d_pair = []
  for d in d_lst:
    d_pair.append((d,))
  txts.append(forall1("entity", d_pair))
  txts.extend(noteq(d_lst))
  for pred in preds:
    e_lst1 = []
    e_lst2 = []
    e_lst0 = []
    e_lst = list(vals[pred])
    for e in e_lst:
      if len(e) == 1:
        e_lst1.append(e)
      elif len(e) == 2:
        e_lst2.append(e)
      else:
        e_lst0.append(e)
    # 1-place predicate
    if e_lst1 != []:
      txt = forall1(pred, e_lst1)
      txts.append(txt)
    # 2-place predicate
    if e_lst2 != []:
      txt = forall2(pred, e_lst2)
      txts.append(txt)
  return(txts)

def notExists(pred, args):
  if len(args) == 2:
    txt = "-exists x y.(" + str(pred) + "(x,y))"
  elif len(args) ==1:
    txt = "-exists x.(" + str(pred) + "(x))"
  else:
    txt = ""
  return(txt)

def structure2formula(model):
  keys = sorted(model.keys())
  values = []
  for key in keys:
    dom = model[key].domain
    vals = model[key].valuation
    #print(' * ' + key)
    txts = forall(dom, vals)
    a_preds = []
    assumptions = []
    for line in txts:
      line2=lexpr(line)
      a_preds.extend(list(line2.predicates()))
      assumptions.append(line2)
    values.append((assumptions, a_preds))
  data = dict(zip(keys, values))
  return(data)

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("--input", default='structure', help='File name of structure data (default=structure)')
  parser.add_argument("--output", default='formula_c', help='File name of formula data (default=formula_c)')
  args = parser.parse_args()

  # load model
  with open(MMI + '/work/' + args.input + '.pkl', 'rb') as f:
    model = pickle.load(f)
  data = structure2formula(model)

  # save
  with open(MMI + '/work/' + args.output + '.pkl', 'wb') as f:
    pickle.dump(data, f, protocol=2)
