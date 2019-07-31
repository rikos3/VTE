# -*- coding: utf-8 -*-

from os.path import expanduser
HOME = expanduser("~")

VTE = HOME + "/VTE"

import sys
sys.path.append(VTE + "/scripts")

import subprocess
import time
from timeout_decorator import timeout, TimeoutError

from word2num import word_to_num as w2n

import make_compound as mcomp
from theoremProver import theorem_proving

import json
import pandas as pd
import numpy as np

# Parse a sentence and output a FOL formula
def parse(text, parser):
    text = w2n(text)
    with open(VTE + '/input.txt', 'w') as f:
        f.write(text)
    start = time.time()
    res = subprocess.run([VTE + "/scripts/parse_multi.sh",parser], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fol = res.stdout.decode('utf-8')
    end = time.time()
    # 複合語の処理
    fol = mcomp.make_compound(fol)
    parse_time = end - start
    return fol, parse_time

# Prover9()を呼び出す
def prove(fol, flag_cap):
    start = time.time()
    lst = theorem_proving(goal=fol, cap=flag_cap, abd=False, prover="prover9")
    end = time.time()
    return(lst, end-start)

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

# Parse a sentence and output a set of images with prover and model-checker
def search(text, parser, keys, flag_cap):
    fol = parse(text, parser)
    formula = fol[0]
    parse_time = round(fol[1], 2)
    prover_results = prove(formula, flag_cap)
    prove_images = prover_results[0]
    prove_time = round(prover_results[1], 2)
    #keys_set = set(keys) - set(noise_lst)
    #prove_set = set(prove_images) - set(noise_lst)
    keys_set = set(keys)
    prove_set = set(prove_images)
    keys_len = len(prove_images)
  
    tpfn = len(keys_set)
    tp = len(keys_set & prove_set)
    tpfp = len(prove_set)
    precision_p, recall_p, f_p = calculate(tp, tpfp, tpfn)
    #res = text, formula, precision_p, recall_p, f_p, parse_time, prove_time
    res = text, formula, precision_p, recall_p, f_p
    return res, prove_images

def run_testsuites(gold_answers, sentences_tags, flag_cap):
  res_lst = []
  prove_images_lst = []

  # label : [total_num. precision, recall, F]
  label_data = {'Con':[0,0,0,0], 'Num':[0,0,0,0], 'Q':[0,0,0,0], 'SpaRel':[0,0,0,0], 'Rel':[0,0,0,0], 'Neg':[0,0,0,0]}
  for sentence, labels in sentences_tags.items():
    if "at least" in sentence.lower():
      parser = "easyccg"
    else:
      parser = "candc"
    answer_keys = gold_answers[sentence]
    results = search(sentence, parser, answer_keys, flag_cap)
    res = results[0]
    res_lst.append(res)
    prove_images_lst.append(results[1])
    if labels[0]:
      label_data['Con'][0] += 1
      label_data['Con'][1] += res[2]
      label_data['Con'][2] += res[3]
      label_data['Con'][3] += res[4]
    if labels[1]:
      label_data['Num'][0] += 1
      label_data['Num'][1] += res[2]
      label_data['Num'][2] += res[3]
      label_data['Num'][3] += res[4]
    if labels[2]:
      label_data['Q'][0] += 1
      label_data['Q'][1] += res[2]
      label_data['Q'][2] += res[3]
      label_data['Q'][3] += res[4]
    if labels[3]:
      label_data['SpaRel'][0] += 1
      label_data['SpaRel'][1] += res[2]
      label_data['SpaRel'][2] += res[3]
      label_data['SpaRel'][3] += res[4]
    if labels[4]:
      label_data['Rel'][0] += 1
      label_data['Rel'][1] += res[2]
      label_data['Rel'][2] += res[3]
      label_data['Rel'][3] += res[4]
    if labels[5]:
      label_data['Neg'][0] += 1
      label_data['Neg'][1] += res[2]
      label_data['Neg'][2] += res[3]
      label_data['Neg'][3] += res[4]

  for key, [num, precision, recall, f] in label_data.items():
    if num == 0:
      print(key + ': ' + str(round(0, 2)) + ", " + str(round(0, 2)) + ", " + str(round(0, 2)))
    else:
      print(key + ': ' + str(round(precision / num, 2)) + ", " + str(round(recall / num, 2)) + ", " + str(round(f / num, 2)))
  print()
  return res_lst, prove_images_lst

if __name__ == '__main__':
  
  with open(VTE + "/eval/gold_answers_GRIM.json", 'r') as f:
    gold_answers = json.load(f)
  with open(VTE + "/eval/sentences_tags_GRIM.json", 'r') as f:
    sentences_tags = json.load(f)

  res1 = run_testsuites(gold_answers, sentences_tags, False)
  array1 = np.array(res1[0])

  res2 = run_testsuites(gold_answers, sentences_tags, True)
  array2 = np.array(res2[0])
  array2 = array2[:,np.array([2,3,4])]
  
  res_lst = np.concatenate([array1, array2], axis=1).tolist()
  df = pd.DataFrame(res_lst, columns=['sentence', 'formula', 'B_Precision', 'B_Recall', 'B_F', 'A_Precision', 'A_Recall', 'A_F'])

  df.to_csv(MMI + "/result/result_test_ACL_GRIM.csv")
