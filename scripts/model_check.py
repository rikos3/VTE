# coding: utf-8

import pickle
import glob
from nltk.sem.logic import *
from nltk.sem import evaluate
from timeout_decorator import timeout, TimeoutError


with open("vte_location.txt", "r") as f:
	VTE = f.read().rstrip("\n")

lexpr = Expression.fromstring

def model_check(goal, flag_cap):
  res_lst = []
  if flag_cap:
    # load model_cap
    with open(VTE + "/work/structure_cap.pkl", 'rb') as f:
      model = pickle.load(f)
  else:
    # load model
    with open(VTE + "/work/structure.pkl", 'rb') as f:
      model = pickle.load(f)

  keys = model.keys()
  #keys = list(set(model.keys()) - set(noise_lst))
  for key in keys:
    m = model[key]
    dom = model[key].domain
    g = evaluate.Assignment(dom)
    goal_preds = lexpr(goal).predicates()
    for pred in goal_preds:
      if m.valuation.get(str(pred)) is None:
        m.valuation[str(pred)] = set()
    res = (m.evaluate(goal, g))
    if res == "Undefined":
      res = False
    if res:
      res_lst.append(key)
  return(res_lst)

def model_check_graph(goal):
  res_lst = []
  # load model
  with open(VTE + "/work/structure_graph_200.pkl", 'rb') as f:
    model = pickle.load(f)

  keys = model.keys()
  #keys = list(set(model.keys()) - set(noise_lst))
  for key in keys:
    m = model[key]
    dom = model[key].domain
    g = evaluate.Assignment(dom)
    goal_preds = lexpr(goal).predicates()
    for pred in goal_preds:
      if m.valuation.get(str(pred)) is None:
        m.valuation[str(pred)] = set()
    res = (m.evaluate(goal, g))
    if res == "Undefined":
      res = False
    if res:
      res_lst.append(key)
  return(res_lst)

def model_check_graph_johnson(goal):
  res_lst = []
  # load model
  with open(VTE + "/work/model_graph_johnson.pkl", 'rb') as f:
    model = pickle.load(f)
  # load fol
  with open(VTE + "/work/fol_graph_johnson_200.pkl", 'rb') as f:
    fol = pickle.load(f)

  keys = fol.keys()
  #keys = list(set(model.keys()) - set(noise_lst))
  for key in keys:
    m = model[key]
    dom = model[key].domain
    g = evaluate.Assignment(dom)
    goal_preds = lexpr(goal).predicates()
    for pred in goal_preds:
      if m.valuation.get(str(pred)) is None:
        m.valuation[str(pred)] = set()
    res = (m.evaluate(goal, g))
    if res == "Undefined":
      res = False
    if res:
      res_lst.append(key)
  return(res_lst)

def model_check_key(key, goal, flag_cap):
  if flag_cap:
    # load model_cap
    with open(VTE + "/work/structure_cap.pkl", 'rb') as f:
      model = pickle.load(f)
  else:
    # load model
    with open(VTE + "/work/structure.pkl", 'rb') as f:
      model = pickle.load(f)

  m = model[key]
  dom = model[key].domain
  g = evaluate.Assignment(dom)
  goal_preds = lexpr(goal).predicates()
  for pred in goal_preds:
    if m.valuation.get(str(pred)) is None:
      m.valuation[str(pred)] = set()
  res = (m.evaluate(goal, g))
  if res == "Undefined":
    res = False
  return(res)
