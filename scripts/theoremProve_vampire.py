# coding: utf-8

from os.path import expanduser
HOME = expanduser("~")

MMI = HOME + "/Multimodal_Inference"
C2L = HOME + "/ccg2lambda"
vampire_dir = MMI + "/vampire"

import subprocess
import sys
sys.path.append(C2L + "/scripts")
sys.path.append(MMI + "/scripts")
from nltk2tptp import convert_to_tptp_proof

import multiprocessing
from multiprocessing import Pool
import re
import pickle
import glob
from nltk.sem.logic import *
from nltk.inference import Prover9

from linguistic_tools import *
from nltk2normal import *
from model2fol import noteq, forall, notExists 
from add_axiom import addAxiom
import make_compound as mcomp

from nltk.corpus import wordnet as wn

# load new_model
with open(MMI + "/data/new_model.pkl", 'rb') as f:
  new_model = pickle.load(f)
# load new_fol
with open(MMI + '/data/new_fol.pkl', 'rb') as f:
  new_fol = pickle.load(f)
# load comments
with open(MMI + '/data/comments.pkl', 'rb') as f:
  comments = pickle.load(f)
# load model
with open(MMI + "/data/model.pkl", 'rb') as f:
  base_model = pickle.load(f)
# load fol
with open(MMI + '/data/fol.pkl', 'rb') as f:
  base_fol = pickle.load(f)
# load fol
with open(MMI + '/data/fol_simple.pkl', 'rb') as f:
  simple_fol = pickle.load(f)
# load words
with open(MMI + '/data/words_elst.pkl', 'rb') as f:
  words_elsts = pickle.load(f)
# load noise_keys
with open(MMI + '/data/noise_keys.pkl', 'rb') as f:
  noise_lst = pickle.load(f)

lexpr = Expression.fromstring

argvs = sys.argv
goal = argvs[1]
caption = argvs[2]
abduction = argvs[3]
circumscription = argvs[4]
polarity = argvs[4]

if caption == 'true':
  flag_cap = True
else:
  flag_cap = False

if abduction == 'true':
  flag_abd = True
else:
  flag_abd = False

if circumscription == 'true':
  flag_cir = True
else:
  flag_cir = False

if polarity == 'true':
  flag_pol = True
else:
  flag_pol = False

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

def split_app(expr, args):
    if isinstance(expr, ConstantExpression):
        return (expr, args)
    elif isinstance(expr, ApplicationExpression):
        f = expr.function
        arg = expr.argument
        args.insert(0, arg)
        return (split_app(f, args))
    else:
        return (expr, args)

# VARIABLE = re.compile(r'([DCNB])(\d+)')
VARIABLE = re.compile(r'([ABCDEFGHIJKLMNOPQRSTUVWZ])(\d+)')

def prove_vampire(formulas):
  fols = convert_to_tptp_proof(formulas)
  tptp_script = ' '.join(fols)
  # print(tptp_script)
  tptp_script = VARIABLE.sub(lambda x: x[1].lower() + x[2], tptp_script)
  # print('======================== tptp_script ====================')
  # print(tptp_script)
  ps = subprocess.Popen(('echo', tptp_script), stdout=subprocess.PIPE)
  output = subprocess.check_output(
            (vampire_dir + '/vampire',),
            stdin=ps.stdout,
            stderr=subprocess.STDOUT)
  ps.wait()
  output_lines = [
    str(line).strip() for line in output.decode('utf-8').split('\n')]
  # print(output_lines[0])
  res = is_theorem_in_vampire(output_lines)
  if res:
    print('================= res =====================')
    print(res)
    print('================= tptp_script =====================')
    print(tptp_script)
  return res

def is_theorem_in_vampire(output_lines):
  if output_lines:
    proof_message = output_lines[0]
    if proof_message == '% Refutation found. Thanks to Tanya!':
      return True
    else:
      return False
  else:
    return False


def prove_fun(args):
  goal, fol, key = args

  g_preds = goal.predicates()
  g_preds = list(g_preds)
  expr_lst = get_atomic_formulas(goal)
  app_data = dict([mcomp.split_app(expr,[]) for expr in expr_lst])

  assumptions, a_preds = fol[key]

  if flag_cap:
    comment = comments[key]
    assumptions.extend(comment)
  words_elst = words_elsts[key]
  # WardNetを使って公理を追加する
  if flag_abd:
    assumptions2, avoid_lst = addAxiom(g_preds, words_elst)
    assumptions.extend(assumptions2)
    diff_preds = set(g_preds) - set(a_preds) - set(avoid_lst) 
  else:
    diff_preds = set(g_preds) - set(a_preds) 
  for pred in list(diff_preds):
    f = lexpr(str(pred))
    try:
      var = app_data[f]
      assumptions.append(lexpr(notExists(pred, var)))
    except:
      pass
  res = prove_vampire(assumptions + [goal])
  if res:
    return key
  else:
    return None

def theoremProve_prover9(goal):
  try:
    goal = lexpr(goal)
    success = True
  except:
    success = False

  if success:

    if flag_cap:
      model = new_model
      fol = new_fol
    else:
      model = base_model
      fol = base_fol

    if flag_cir:
      model = base_model
      fol = base_fol
    else:
      model = base_model
      fol = simple_fol

    if flag_pol:
      if check_polarity(goal):
        model = base_model
        fol = simple_fol
      else:
        model = base_model
        fol = base_fol
    else:
      pass

    #keys = model.keys()
    keys = sorted(list(set(model.keys()) - set(noise_lst)))
  
    lst = [(goal, fol, key) for key in keys]

    # print(len(lst))
    # CPUの数だけ同時にプロセスを実行する
    pool = Pool(multiprocessing.cpu_count())
    res = pool.map(prove_fun, lst) 
    res_lst = [key for key in res if key]
    for key in res_lst: 
      print(key)
    return(res_lst)
  else:
    res_lst = []
    print(res_lst)
    return(res_lst)

if __name__ == '__main__':
  theoremProve_prover9(goal)

def theoremProve_prover9_key(key, model, goal, flag):
    res_lst = []
    goal = lexpr(goal)
    expr_lst, variables = mcomp.split(goal, [], [])
    app_data = dict([mcomp.split_app(expr,[]) for expr in expr_lst])

    g_preds = goal.predicates()
    g_preds = list(g_preds)
    assumptions, a_preds = fol[key]
    comment = comments[key]
    assumptions.extend(comment)
    words_elst = words_elsts[key]
    if flag:
        assumptions2, avoid_lst = addAxiom(g_preds, words_elst)
        assumptions.extend(assumptions2)
    else:
        avoid_lst = []
    diff_preds = set(g_preds) - set(a_preds) - set(avoid_lst) 
    for pred in list(diff_preds):
        try:
          var = app_data[pred]
          assumptions.append(lexpr(notExists(pred, var)))
        except:
          pass
    assumptions = list(set(assumptions))
    try:
      res = Prover9(timeout=10).prove(goal, assumptions)
    except:
      res = 'ProveError'
    return(res)
