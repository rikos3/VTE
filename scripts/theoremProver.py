# coding: utf-8

from os.path import expanduser
HOME = expanduser("~")

VTE = HOME + "/VTE"
C2L = HOME + "/ccg2lambda"

import sys
sys.path.append(C2L + "/scripts")
sys.path.append(VTE + "/scripts")

import argparse
from nltk.sem.logic import *

from linguistic_tools import *
from nltk2normal import *

from theoremProver_prover9 import theoremProver_prover9 
#from theoremProver_prover9 import theoremProver_vampire

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

def theorem_proving(goal, abd, cap, prover):

  try:
    goal = lexpr(goal)
    success = True
  except:
    success = False

  if success:

    if check_polarity(goal):
      formula = VTE + '/work/formula_s.pkl'
    else:
      formula = VTE + '/work/formula_c.pkl'

    if prover == 'prover9':
      theoremProver_prover9(goal=goal, formula=formula, abd=abd, cap=cap, mace4=False)
    elif prover == 'prover9+mace4':
      theoremProver_prover9(goal=goal, formula=formula, abd=abd, cap=cap, mace4=True)
#    elif prover == 'vampire':
#      theoremProving_vampire(goal=goal, formula=formula, abd=abd, cap=cap)

  else:
    print('ERROR')

if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument('--goal', required=True)
  parser.add_argument('--abd', default=False)
  parser.add_argument('--cap', default=False)
  parser.add_argument('--prover', default='prover9', choices=['prover9', 'prover9+mace4', 'vampire'])
  args = parser.parse_args()

  theorem_proving(args.goal, args.abd, args.cap, args.prover)
