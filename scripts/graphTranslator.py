# coding: utf-8

import json
import pickle
import re
from nltk.sem import Valuation, Model
from itertools import groupby
from operator import itemgetter
import string
from nltk.stem.snowball import SnowballStemmer 

stemmer = SnowballStemmer("english")

from os.path import expanduser, splitext

with open("../vte_location.txt", "r") as f:
	VTE = f.read().rstrip("\n")

def get_newEntity(domain):
  i = 1
  new_entity = 'dd' + str(i)
  while {new_entity}.issubset(domain):
    i += 1
    new_entity = 'dd' + str(i)
  return(new_entity)

if __name__ == '__main__':

  with open(VTE + "/data/sg_test_annotations.json") as f:
    data = json.load(f)

  with open(VTE + "/data/test_id_200.json") as f:
    id_lst = json.load(f)
  
  models = [{}, {}, {}]
  word_data = {}

  char_lst = list(string.ascii_letters)

  for index, d in enumerate(data):

    filename = d['filename']
    key, ext = splitext(filename)

    if key in id_lst:
      obj_data = d.get('objects', {})
      id_entity = {}
      dom = set()
      val = []
      val_obj = []
      val_obj_att = []
      relations = []
  
      for obj_id, obj in enumerate(d['objects']):
        obj_name = obj['names'][0].replace('the ','').replace('.', '').replace(',', '_').replace('-', '_').replace(' ', '_').replace('&', '_and_').replace("'s", "_")
        obj_name = re.sub(r'_[0-9]*', '', obj_name)
        while obj_name[0] == '_':
          obj_name = obj_name[1:]
        entity = get_newEntity(dom)
        id_entity[obj_id] = entity
        dom.add(entity)
        obj_lst = obj_name.split('_')
        for obj_name in obj_lst:
          if not obj_name in char_lst:
            val.append((obj_name, [(entity,)]))
            val_obj.append((obj_name, [(entity,)]))
            val_obj_att.append((obj_name, [(entity,)]))
  
          for att in obj['attributes']:
            att_name_lst = att['attribute'].split()
            if 'ing' in att_name_lst[0]:
              att_name = stemmer.stem(att_name_lst[0])
            else:
              att_name = att_name_lst[0]
            for att_name1 in att_name_lst[1:]:
              if 'ing' in att_name1:
                att_name += ' ' + stemmer.stem(att_name1)
              else:
                att_name = ' ' + att_name1
  
            att_name = att_name.replace('.', '').replace(',', '_').replace('-', '_').replace(' ', '_').replace('&', '_and_')
            while att_name[0] == '_':
              att_name = att_name[1:]
            if 'not_' in att_name:
              att_lst = ['-' + att_name[4:]]
            else:
              att_lst = att_name.split('_')
              att_lst.append(att_name)
            for att_name in att_lst:
              if not att_name in char_lst:
                val.append((att_name, [(entity,)]))
                val_obj_att.append((att_name, [(entity,)]))
  
      for rel in d['relationships']:
        entity1 = id_entity.get(rel['objects'][0])
        entity2 = id_entity.get(rel['objects'][1])
        rel_name_lst = rel['relationship'].split()
        if 'ing' in rel_name_lst[0]:
          rel_name = stemmer.stem(rel_name_lst[0])
        elif 'has' == rel_name_lst[0]:
          rel_name = 'have'
        else:
          rel_name = rel_name_lst[0]
        for rel_name1 in rel_name_lst[1:]:
          if 'ing' in rel_name1:
            rel_name += ' ' + stemmer.stem(rel_name1)
          elif 'has' == rel_name1:
            rel_name += ' ' + 'have'
          else:
            rel_name += ' ' + rel_name1
        rel_name = rel_name.replace('.', '').replace(',', '_').replace('-', '_').replace(' ', '_').replace('&', '_and_')
        while rel_name[0] == '_':
          rel_name = rel_name[1:]
        
        if '_next_to' in rel_name:
          rel_lst = rel_name.split('_', 1)
          val.append((rel_lst[0], [(entity1,)]))
          val_obj_att.append((rel_lst[0], [(entity1,)]))
          val.append((rel_lst[1], [(entity1, entity2)]))
        elif rel_name in ['next_to', 'in_front_of', 'left_of' 'right_of', 'on_top_of', 'front_of']:
          val.append((rel_name, [(entity1, entity2)]))
        else:
          if (rel_name is not None and entity1 is not None and entity2 is not None and not rel_name in char_lst):
            val.append((rel_name, [(entity1, entity2)]))
          if '_' in rel_name:
            rel_lst = rel_name.split('_')
            rel_lst = [rel_name for rel_name in rel_lst if (not rel_name in char_lst and not rel_name in ["is","are","an", "the"])]
            if len(rel_lst) == 2:
              val.append((rel_lst[0], [(entity1,)]))
              val_obj_att.append((rel_lst[0], [(entity1,)]))
              val.append((rel_lst[1], [(entity1, entity2)]))
            else:
              for rel_name in rel_lst[:-1]:
                val.append((rel_name, [(entity1,)]))
                val_obj_att.append((rel_name, [(entity1,)]))
              val.append((rel_lst[-1], [(entity1, entity2)]))
  
      vals = [val_obj, val_obj_att, val]
      for i in range(len(vals)):
        data = {}
        val0 = vals[i]
        val2 = []
        for name, g in groupby(sorted(val0), itemgetter(0)):
          e_len1 = []
          e_len2 = []
          for name1, entities1 in g:
            if len(entities1[0]) == 1:
              e_len1.extend(entities1)
            elif len(entities1[0]) == 2:
              e_len2.extend(entities1)
          if len(list(set(e_len1))) > len(list(set(e_len2))):
            e_set = set(e_len1)
            data[name] = e_len1
          else:
            e_set = set(e_len2)
            data[name] = e_len2
          val2.append((name, e_set))
        models[i][key] = Model(dom, Valuation(val2))  
        word_data[key] = data

  #save model
  #with open(VTE + '/work/structure_g_obj.pkl', 'wb') as f:
  #  pickle.dump(models[0], f, protocol=2)

  #save model
  #with open(VTE + '/work/structure_g_obj_att.pkl', 'wb') as f:
  #  pickle.dump(models[1], f, protocol=2)

  #save model
  with open(VTE + '/work/structure_graph_200.pkl', 'wb') as f:
    pickle.dump(models[2], f, protocol=2)

  # save words
  with open(VTE + '/work/words_elst_graph_200.pkl', 'wb') as f:
    pickle.dump(word_data, f, protocol=2)
