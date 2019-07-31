# -*- coding: utf-8 -*-

# image(graph) + captions entails an sentence

from os.path import expanduser
HOME = expanduser("~")

VTE = HOME + "/VTE"

import sys
sys.path.append(VTE + "/scripts")

import pandas as pd
import pickle

# load sentences_tags.csv
# sentence, Con, Num, Q, Rel, Neg
sentence_data = pd.read_csv(VTE + "/eval/sentences_tags.csv")

# load system_result
# key: sentence, value:image ID list
with open(VTE + '/result/predictions.pkl', 'rb') as f:
  res_system = pickle.load(f)

# load human_result
# key: sentence, value:image ID list
with open(VTE + '/eval/annotations.pkl', 'rb') as f:
  res_human = pickle.load(f)

def calculate(tp, tpfp, tpfn):
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
  return(precision, recall, f)

def run_testsuites():
  label_data = {'Con':[0,0,0,0], 'Num':[0,0,0,0], 'Q':[0,0,0,0], 'Rel':[0,0,0,0], 'Neg':[0,0,0,0]}
  for index, line in sentence_data.iterrows():
    sentence = line['sentence']
    human_set = set(res_human[sentence])
    system_set = set(res_system[sentence])
    tp = len(human_set & system_set)
    tpfp = len(system_set)
    tpfn = len(human_set)
    res = calculate(tp, tpfp, tpfn)
    if line['Con']:
      label_data['Con'][0] += 1
      label_data['Con'][1] += res[0]
      label_data['Con'][2] += res[1]
      label_data['Con'][3] += res[2]
    if line['Num']:
      label_data['Num'][0] += 1
      label_data['Num'][1] += res[0]
      label_data['Num'][2] += res[1]
      label_data['Num'][3] += res[2]
    if line['Q']:
      label_data['Q'][0] += 1
      label_data['Q'][1] += res[0]
      label_data['Q'][2] += res[1]
      label_data['Q'][3] += res[2]
    if line['Rel']:
      label_data['Rel'][0] += 1
      label_data['Rel'][1] += res[0]
      label_data['Rel'][2] += res[1]
      label_data['Rel'][3] += res[2]
    if line['Neg']:
      label_data['Neg'][0] += 1
      label_data['Neg'][1] += res[0]
      label_data['Neg'][2] += res[1]
      label_data['Neg'][3] += res[2]


  for key, [num, precision, recall, f] in label_data.items():
    if num == 0:
      print(key + ': ' + str(round(0, 2)) + ", " + str(round(0, 2)) + ", " + str(round(0, 2)) + ", " + str(num))
    else:
      print(key + ': ' + str(round(precision / num, 2)) + ", " + str(round(recall / num, 2)) + ", " + str(round(f / num, 2)) + ", " + str(num))
  print()

  return None

if __name__ == '__main__':
  run_testsuites()

