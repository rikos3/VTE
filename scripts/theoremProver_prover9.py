# coding: utf-8

from os.path import expanduser
HOME = expanduser("~")

VTE = HOME + "/VTE"
C2L = HOME + "/ccg2lambda"

import sys
sys.path.append(C2L + "/scripts")
sys.path.append(VTE + "/scripts")

import multiprocessing
from multiprocessing import Pool, Queue, Process

import argparse
import pickle
from nltk.sem.logic import *
from nltk.inference import Prover9, Mace

from linguistic_tools import *
from nltk2normal import *
from simpleTranslator import notExists 
from add_axiom import addAxiom
import make_compound as mcomp

lexpr = Expression.fromstring

def prove_fun(queue, i, is_prover, goal, key):

  g_preds = goal.predicates()
  g_preds = list(g_preds)
  expr_lst = get_atomic_formulas(goal)
  app_data = dict([mcomp.split_app(expr,[]) for expr in expr_lst])

  assumptions, a_preds = formulas[key]

  if flag_cap:
    comment = comments[key]
    assumptions.extend(comment)
  words_elst = words_elsts[key]

  if flag_abd:
    assumptions2, avoid_lst = addAxiom(g_preds, words_elst)
    assumptions.extend(assumptions2)
    diff_preds = set(g_preds) - set(a_preds) - set(avoid_lst) 
  else:
    diff_preds = set(g_preds) - set(a_preds) 

  for pred in list(diff_preds):
    f = lexpr(str(pred))
    var = app_data.get(f)
    if var is not None:
      assumptions.append(lexpr(notExists(pred, var)))
  if is_prover:
    res = Prover9(timeout=1).prove(goal, assumptions)
  else:
    res = not Mace(end_size=10).build_model(goal, assumptions)
  queue.put((i, is_prover, key if res else None))


def prover9(goal, flag_sub):
  queue = Queue()
  prover_processes = []

  for i, key in enumerate(keys):
    prover_processes.append(Process(target=prove_fun, args=(queue, i, True, goal, key)))
    prover_processes[-1].start()

  done = [False for _ in keys]
  res = []
  while not all(done):
    if queue.empty():
      continue
    i, is_prover, key = queue.get()

    if done[i]:
      continue
    else:
      done[i] = True

    if key is not None:
      res.append(key)
      if not flag_sub:
        print(key)

  return(res)


def prover9_mace4(goal):
  queue = Queue()
  prover_processes = []
  modelbuilder_processes = []
  for i, key in enumerate(keys):
    prover_processes.append(Process(target=prove_fun, args=(queue, i, True, goal, key)))
    modelbuilder_processes.append(Process(target=prove_fun, args=(queue, i, False, goal, key)))
    prover_processes[-1].start()
    modelbuilder_processes[-1].start()

  done = [False for _ in keys]
  res = []
  while not all(done):
    if queue.empty():
      continue
    i, is_prover, key = queue.get()

    if done[i]:
      continue
    else:
      done[i] = True

    if is_prover:
      modelbuilder_processes[i].terminate()
    else:
      prover_processes[i].terminate()

    if key is not None:
      res.append(key)
      print(key)

  return(res)

def check_existence(goal):
  if isinstance(goal, ExistsExpression):
    g_term = goal.term
    if isinstance(g_term, AndExpression):
      if ((isinstance(g_term.first, AndExpression) or isinstance(g_term.first, ApplicationExpression)) and isinstance(g_term.second, AllExpression)):
        sub_goal = ExistsExpression(goal.variable, g_term.first)
        goal = g_term.second
        sub_res = prover9(sub_goal, True)
        keys = [key for key in sub_res if key]
  return(goal)

def theoremProver_prover9(goal, formula, abd, cap, mace4):

  global flag_cap
  global flag_abd
  flag_cap = cap
  flag_abd = abd

  global formulas
  with open(formula, "rb") as f:
    formulas = pickle.load(f)

  global words_elsts
  with open(VTE + "/work/words_elst.pkl", "rb") as f:
    words_elsts = pickle.load(f)
  if flag_cap:
    global comments
    with open(VTE + "/work/comments.pkl", "rb") as f:
      comments = pickle.load(f)

  global keys
  keys = formulas.keys()

  try:
    goal = check_existence(lexpr(goal))
  except:
    goal = check_existence(goal)


  if mace4:
    prover9_mace4(goal)
  else:
    prover9(goal, False)
