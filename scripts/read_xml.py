import xml.etree.ElementTree as ET

from nltk.corpus import wordnet as wn
from nltk.wsd import lesk
from nltk.stem import WordNetLemmatizer
lem = WordNetLemmatizer()

def use_lesk(xmlfile):
  tree = ET.ElementTree(file=xmlfile)

  root = tree.getroot()

  res = []

  for document in root:
    for sentences in document:
      for sentence in sentences:
        sent = []
        pair_lst = []
        data = {}
        for tokens in sentence:
          if(tokens.tag == 'tokens'):
            for token in tokens:
              word = token.attrib['surf']
              sent.append(word)
              pos = token.attrib['pos']
              pair_lst.append((word, pos))
            for word, pos in pair_lst:
              if(pos.startswith('NN')):
                lemma = lem.lemmatize(word, pos='n')
                data[lemma] = (lesk(sent, word, wn.NOUN), 'n')
              elif(pos.startswith('VB')):
                lemma = lem.lemmatize(word, pos='v')
                data[lemma] = (lesk(sent, word, wn.VERB), 'v')
              elif(pos.startswith('JJ')):
                lemma = lem.lemmatize(word, pos='a')
                data[lemma] = (lesk(sent, word, wn.ADJ), 'a')
              elif(pos.startswith('RB')):
                data[word] = (lesk(sent, word, wn.ADV), '')
              else:
                pass
            res.append(data)
          else:
              pass
  return(res)
