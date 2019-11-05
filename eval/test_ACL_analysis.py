# -*- coding: utf-8 -*-


with open("../vte_location.txt", "r") as f:
	VTE = f.read().rstrip("\n")
with open("../ccg2lambda_location.txt", "r") as f:
	C2L = f.read().rstrip("\n")

import sys
sys.path.append(C2L + "/scripts")
sys.path.append(VTE + "/scripts")

from nltk2normal import *
import make_compound as mcomp
from word2num import word_to_num as w2n
import subprocess
from nltk.sem.logic import *

import pickle
import pandas as pd

lexpr = Expression.fromstring

with open(VTE + "/data/fol_graph_johnson.pkl", 'rb') as f:
  sg_fol = pickle.load(f)

sentence_data = pd.read_csv(VTE + '/data/sentences.csv')
sentences = sentence_data['sentence']

# load system_result
# key: sentence, value:image ID list
with open(VTE + '/data/answer_johnson_200_abd_2.pkl', 'rb') as f:
  res_system = pickle.load(f)

# load human_result
# key: sentence, value:image ID list
with open(VTE + '/data/human_johnson_200_2.pkl', 'rb') as f:
  res_human = pickle.load(f)

# Parse a sentence and output a FOL formula
def parse(text, parser):
  # 数詞の処理
  text = w2n(text)
  # 入力文を input.txt に書き込む
  with open(VTE + '/input.txt', 'w') as f:
    f.write(text)
  res = subprocess.run([VTE + "/scripts/parse_multi.sh",parser], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  fol = res.stdout.decode('utf-8')
  # 複合語の処理
  fol = mcomp.make_compound(fol)
  return fol

for sentence in sentences:
  images_human = res_human[sentence]
  images_system = res_system[sentence]['proposed_model']
  images = list(set(images_human) - set(images_system))
  if images != []:
    if 'at least' in sentence.lower():
      formula = parse(sentence, 'easyccg')
    else:
      formula = parse(sentence, 'candc')
    formula = lexpr(formula)
    expr_lst = get_atomic_formulas(formula)
    for key in images:
      if len(set(expr_lst) - set(sg_fol[key][0])) == 0:
        print(key)
  else:
    pass
