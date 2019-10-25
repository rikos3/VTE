#!/usr/bin/python3
# -*- coding: utf-8 -*-

from os.path import expanduser
HOME = expanduser("~")

C2L = HOME + "/ccg2lambda"
MMI = HOME + "/multimodal_inference"

import cgi

import sys
sys.path.append(C2L + "/scripts")
sys.path.append(MMI + "/scripts")

import subprocess
import time
import math

from lxml import etree
from nltk.sem.logic import *
from visualization_tools import convert_root_to_mathml
from word2num import word_to_num as w2n

import theoremProve_prover9 as tpp9
import model_check as mc
import make_compound as mcomp

def prove(fol):
    start = time.time()
#    res = subprocess.Popen(["python", MMI + "/scripts/theoremProve_prover9.py", fol, caption, abduction, circumscription, ''], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    lst = res.stdout.readlines()
    lst = tpp9.theoremProve_prover9(fol, flag_cap, flag_abd)
    end = time.time()
    return(lst, end-start)

def model_check(fol):
    start = time.time()
    lst = mc.model_check(fol, flag_cap)
    end = time.time()
    return(lst, end-start)

print('Content-type: text/html\n')

html = """
<!DOCTYPE html>
<meta charset="utf-8" />
<html>
<head>
<title>output</title>
<style>
h1 {
font-size: 1.5em;
}
h2 {
font-size: 1em;
}
</style>
</head>
<body>
<input type="button" onclick="location.href='../index.html'" value="戻る"><br>
<center>%s</center>
</body>
"""

# get fol
form = cgi.FieldStorage()
input_text = form.getfirst('input','')

# select parser
parser = form.getfirst('parser','')

caption = form.getfirst('caption','')
if caption == 'true':
  flag_cap = True
  cap = 'ON'
else:
  flag_cap = False
  cap = 'OFF'

abduction = form.getfirst('abduction','')
if abduction == 'true':
  flag_abd = True
  abd = 'ON'
else:
  flag_abd = False
  abd = 'OFF'

if input_text == 'text':
    text = form.getvalue('text','')
    text = w2n(text)
    with open(MMI + '/input.txt', 'w') as f:
        f.write(text)
    start = time.time()
    res = subprocess.run([MMI + "/scripts/parse_multi.sh",parser], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fol = res.stdout.decode('utf-8')
    end = time.time()
    time1 = end-start
elif input_text == 'fol':
    text = form.getvalue('text','')
    fol = text
    time1 = 0

fol = mcomp.make_compound(fol)

body_sem = '<h1> Input: ' + text + '<br> FOL: ' + fol + '</h1><br>'
print(html % (body_sem))

html_images = """
<center>%s</center>
</html>
"""

# select model_check / prover
selector = form.getfirst('select','')
if selector == 'model_check':
    lst, time2 = model_check(fol)
elif selector == 'prover':
    lst, time2 = prove(fol)
    #lst = [x.decode('utf-8').replace("\n","") for x in lst]

num = len(lst)
body = '<h2>' + selector + '<br>' \
    + 'Number of images: ' + str(num) \
    + '&nbsp; Parsing: ' + str(round(time1)) + ' sec' \
    + '&nbsp; Proving: ' + str(round(time2)) + ' sec<br>' \
    + 'Abduction: ' + abd + '&nbsp; Caption: ' + cap + '</h2><br>'
for image in lst:
    img = '<a href="../grim/data/' + image + '.txt" target="_blank">' + '<img src="../grim/image/' + image + '.jpg" title="' + image + '" height="150"></a>&nbsp;'
    body += img
print(html_images % (body))

with open(MMI + "/input.txt." + parser + ".sem.xml") as f:
    root = etree.parse(f)
    html_str = convert_root_to_mathml(root)
    print(html_str)
