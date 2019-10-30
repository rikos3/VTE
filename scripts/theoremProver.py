# coding: utf-8

with open("vte_location.txt", "r") as f:
  VTE = f.read().rstrip("\n")
with open("ccg2lambda_location.txt", "r") as f:
  C2L = f.read().rstrip("\n")

import sys
sys.path.append(C2L + "/scripts")
sys.path.append(VTE + "/scripts")

import argparse
from nltk.sem.logic import *

from linguistic_tools import *
from nltk2normal import *

import theoremProver_prover9 as tpp9

lexpr = Expression.fromstring

def check_polarity(expression):
  if isinstance(expression, ApplicationExpression):
    return True
  elif isinstance(expression, EqualityExpression):
    return True
  elif isinstance(expression, AndExpression):
    pol1 = check_polarity(expression.first)
    pol2 = check_polarity(expression.second)
    polarity = pol1 and pol2
    return polarity
  elif isinstance(expression, OrExpression):
    pol1 = check_polarity(expression.first)
    pol2 = check_polarity(expression.second)
    polarity = pol1 and pol2
    return polarity
  elif isinstance(expression, ImpExpression):
    pol1 = check_polarity(expression.first)
    pol2 = check_polarity(expression.second)
    polarity = not pol1 and pol2
    return polarity
  elif isinstance(expression, NegatedExpression):
    body = expression.term
    if isinstance(body, EqualityExpression):
      return True
    else:
      polarity = not check_polarity(body)
      return polarity
  elif isinstance(expression, ExistsExpression):
    body = expression.term
    polarity = check_polarity(body)
    return polarity 
  elif isinstance(expression, AllExpression):
    body = expression.term
    polarity = check_polarity(body)
    return polarity 
  elif isinstance(expression, ConstantExpression):
    if expression.variable == Variable('false'):
      return False
    else:
      return True
  else:
    return True

def theorem_proving(goal, dataset, abd, cap, prover, output):

  try:
    goal = lexpr(goal)
    success = True
  except:
    success = False

  if success:

    if check_polarity(goal):
      if dataset == 'grim':
        formula = VTE + '/work/formula_s.pkl'
      elif dataset == 'visual_genome':
        formula = VTE + '/work/formula_vg_s.pkl'
    else:
      if dataset == 'grim':
        formula = VTE + '/work/formula_c.pkl'
      elif dataset == 'visual_genome':
        formula = VTE + '/work/formula_vg_c.pkl'

    if prover == 'prover9':
      #return(tpp9.theorem_proving(goal=goal, formula=formula, abd=abd, cap=cap, mace4=False, output=output))
      res = list(set(tpp9.theorem_proving(goal=goal, formula=formula, dataset=dataset, abd=abd, cap=cap, mace4=False, output=output)) - {"beggars-210035_640", "still-life-379858_640"})
      return(res)
    elif prover == 'prover9+mace4':
      res = list(set(tpp9.theorem_proving(goal=goal, formula=formula, dataset=dataset, abd=abd, cap=cap, mace4=False, output=output)) - {"beggars-210035_640", "still-life-379858_640"})
      return(res)
#    elif prover == 'vampire':
#      theoremProving_vampire(goal=goal, formula=formula, abd=abd, cap=cap)

  else:
    print('ERROR')

if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument('--goal', required=True)
  parser.add_argument('--dataset', default='grim', choices=['grim', 'visual_genome'])
  parser.add_argument('--abd', default=False)
  parser.add_argument('--cap', default=False)
  parser.add_argument('--prover', default='prover9', choices=['prover9', 'prover9+mace4', 'vampire'])
  parser.add_argument('--output', default=True)
  args = parser.parse_args()

  theorem_proving(args.goal, args.dataset, args.abd, args.cap, args.prover, args.output)
