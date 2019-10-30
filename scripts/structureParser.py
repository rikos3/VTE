# coding: utf-8


with open("../vte_location.txt", "r") as f:
	VTE = f.read().rstrip("\n")
GRIM = HOME + "/grim/data"

import json
import pickle
import re
from nltk.sem import Valuation, Model

with open(VTE + "/data/grim.json", "r") as f:
  grim_lst = json.load(f)

# for 1-place predicate
# f(1,n_man_1,[d1, d2]) --> (man, {d1, d2}), {man, man.n.1}, {man.n.1: {d1, d2}}
def make_lst1(pos, s):
  pair = re.findall('f\(1,' + pos + '_(.*)_(.),\[([^\[].+)\]',s)
  lst = []
  data = {}
  for name, num, entities in pair:
    e_lst = entities.replace("])","").split(',')
    word = name + "." + pos + "." + num.zfill(2)
    e_lst2 = []
    for e in e_lst:
      e_lst2.append((e[0] + e,))
    lst.append((name, set(e_lst2)))
    data[word] = e_lst2
  return(lst, data)

# Stemming(touches --> touch)
stems = {"touches": "touch",
         "supports": "support",
         "occludes": "occlude"}

# for 2-place predicate
# f(2,s_touches,[(d1,d2),(d2,d1)]) --> (touch, {(d1,d2),(d2,d1)})
def make_lst2(pos, s):
  pair = re.findall('f\(2,' + pos + '_(.*),\[([^\[].+)\]',s)
  lst = []
  data = {}
  for name, entities in pair:
    if name in stems:
      name = stems[name]
    pairs = entities.replace("),(",").(").replace(")])",")").split(".")
    p_lst = []
    for p in pairs:
      p_lst.append(re.findall('\((.+),(.+)\)',p)[0])
    p_lst2 = []
    for p1, p2 in p_lst:
      p_lst2.append((p1[0] + p1, p2[0] + p2))
    lst.append((name, set(p_lst2)))
    data[name] = p_lst2
  return(lst, data)

# (touch, {(d1,d2)}) --> (touch, {(d1,d2),(d2,d1)})
def add_entity(data):
  for name, p_lst in data.items():
    if name in ['touch', 'near']:
      for (e1, e2) in p_lst:
        rev_pair = (e2, e1)
        if not rev_pair in p_lst:
          p_lst.append(rev_pair)
      data[name] = p_lst
  return(data)
        
def model_parser(model):
  with open(model) as f:
    data = {}
    s = f.read()
    # w1 -> a1
    s = re.sub("w([0-9])", "a\\1", s)
    n_lst, data_n = make_lst1('n', s)
    a_lst, data_a = make_lst1('a', s)
    s_lst, data_s = make_lst2('s', s)
    data_s = add_entity(data_s)
    v = n_lst + a_lst + s_lst
    data.update(data_n)
    data.update(data_a)
    data.update(data_s)
  return(v, data)

if __name__ == '__main__':

  model_data = {}
  word_data = {}
  for model_id in grim_lst:
    v, data = model_parser(GRIM + '/' + model_id + '.mod')
    model_data[model_id] = v
    word_data[model_id] = data
  
  # construct a new Model.
  model = {}
  for model_id in grim_lst:
    val = Valuation(model_data[model_id])
    dom = val.domain
    m = Model(dom, val)
    model[model_id] = m
  
  # save model
  with open(VTE + '/work/structure.pkl', 'wb') as f:
    pickle.dump(model, f, protocol=2)
  
  # save words
  with open(VTE + '/work/words_elst.pkl', 'wb') as f:
    pickle.dump(word_data, f, protocol=2)
