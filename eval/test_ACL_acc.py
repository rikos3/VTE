# 画像(graph) + キャプション |- 文

# -*- coding: utf-8 -*-


with open("../vte_location.txt", "r") as f:
	VTE = f.read().rstrip("\n")

import sys
sys.path.append(VTE + "/scripts")

import subprocess
import time
from timeout_decorator import timeout, TimeoutError

from word2num import word_to_num as w2n

import make_compound as mcomp
import theoremProve_prover9_for_test as tpp9

import pandas as pd
import pickle

import numpy as np

# load fol
with open(VTE + '/data/fol_graph_johnson_200.pkl', 'rb') as f:
  fol = pickle.load(f)

# load sentences
# sentence, Con, Num, Q, Rel, Neg
sentence_data = pd.read_csv(VTE + "/data/sentences_2.csv")

# load system_result
# key: sentence, value:image ID list
with open(VTE + '/data/answer_johnson_200_2.pkl', 'rb') as f:
  res_system = pickle.load(f)

# load human_result
# key: sentence, value:image ID list
with open(VTE + '/data/human_johnson_200_2.pkl', 'rb') as f:
  res_human = pickle.load(f)


def calculate(tp, tn, tpfp, tpfn, tptnfpfn):
  try:
    precision = round(tp / tpfp * 100, 2)
  except:
    precision = round(0, 2)
  try:
    recall = round(tp / tpfn * 100, 2)
  except:
    recall = round(0, 2)
  try:
    f = round(2 * recall * precision / (recall + precision), 2)
  except:
    f = round(0, 2)
  try:
    acc = round((tp + tn) / (tptnfpfn) * 100, 2)
  except:
    acc = round(0, 2)
  return(precision, recall, f, acc)

def run_testsuites():
  select_lst = ['obj_att_model', 'obj_att_rel_model', 'proposed_model']
  # label : [total_num. precision, recall, F]
  label_data0 = {'Con':[0,0,0,0,0], 'Num':[0,0,0,0,0], 'Q':[0,0,0,0,0], 'Rel':[0,0,0,0,0], 'Neg':[0,0,0,0,0]}
  label_data1 = {'Con':[0,0,0,0,0], 'Num':[0,0,0,0,0], 'Q':[0,0,0,0,0], 'Rel':[0,0,0,0,0], 'Neg':[0,0,0,0,0]}
  label_data2 = {'Con':[0,0,0,0,0], 'Num':[0,0,0,0,0], 'Q':[0,0,0,0,0], 'Rel':[0,0,0,0,0], 'Neg':[0,0,0,0,0]}
  label_data = dict(zip(select_lst, [label_data0, label_data1, label_data2]))
  for index, line in sentence_data.iterrows():
    sentence = line['sentence']
    human_set = set(res_human[sentence])
    keys_set = set(fol.keys())
    for select in select_lst:
      system_set = set(res_system[sentence][select])
      tp = len(human_set & system_set)
      tn = len(keys_set - (human_set | system_set))
      tpfp = len(system_set)
      tpfn = len(human_set)
      tptnfpfn = len(keys_set)
      res = calculate(tp, tn, tpfp, tpfn, tptnfpfn)
      if line['Con']:
        label_data[select]['Con'][0] += 1
        label_data[select]['Con'][1] += res[0]
        label_data[select]['Con'][2] += res[1]
        label_data[select]['Con'][3] += res[2]
        label_data[select]['Con'][4] += res[3]
      if line['Num']:
        label_data[select]['Num'][0] += 1
        label_data[select]['Num'][1] += res[0]
        label_data[select]['Num'][2] += res[1]
        label_data[select]['Num'][3] += res[2]
        label_data[select]['Num'][4] += res[3]
      if line['Q']:
        label_data[select]['Q'][0] += 1
        label_data[select]['Q'][1] += res[0]
        label_data[select]['Q'][2] += res[1]
        label_data[select]['Q'][3] += res[2]
        label_data[select]['Q'][4] += res[3]
      if line['Rel']:
        label_data[select]['Rel'][0] += 1
        label_data[select]['Rel'][1] += res[0]
        label_data[select]['Rel'][2] += res[1]
        label_data[select]['Rel'][3] += res[2]
        label_data[select]['Rel'][4] += res[3]
      if line['Neg']:
        label_data[select]['Neg'][0] += 1
        label_data[select]['Neg'][1] += res[0]
        label_data[select]['Neg'][2] += res[1]
        label_data[select]['Neg'][3] += res[2]
        label_data[select]['Neg'][4] += res[3]


  for select in select_lst:
    print(select)
    for key, [num, precision, recall, f, acc] in label_data[select].items():
      if num == 0:
        print(key + ': ' + str(round(0, 2)) + ", " + str(round(0, 2)) + ", " + str(round(0, 2)) + ", "  + str(round(0, 2)) + ", " + str(num))
      else:
        print(key + ': ' + str(round(precision / num, 2)) + ", " + str(round(recall / num, 2)) + ", " + str(round(f / num, 2)) + ", " + str(round(acc / num, 2))+ ", " + str(num))
    print()

  return None

if __name__ == '__main__':
  run_testsuites()

#save 
#with open(VTE + '/data/resulti_test_ACL.pkl', 'wb') as f:
#  pickle.dump(res_data, f, protocol=2)
