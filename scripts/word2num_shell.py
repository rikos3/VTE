from word2num import word_to_num as w2n

import sys
argvs = sys.argv

with open(argvs[1]) as f:
    text = f.read()
    res = w2n(text).replace('.', '.\n')
with open(argvs[2], 'w') as f:
    f.write(res)
