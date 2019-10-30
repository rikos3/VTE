import glob

file_lst = glob.glob("*.py")
file_lst.remove("modify.py")

for path in file_lst:
  with open(path, "r") as f:
    texts = f.read()

  texts = texts.replace('from os.path import expanduser\n', '')
  texts = texts.replace('HOME = expanduser("~")\n', '')
  texts = texts.replace('MMI = HOME + "/multimodal_inference"', 'with open("../vte_location.txt", "r") as f:\n\tVTE = f.read().rstrip("\\n")')
  texts = texts.replace('MMI', 'VTE')
  texts = texts.replace('VTE = HOME + "/VTE"', 'with open("../vte_location.txt", "r") as f:\n\tVTE = f.read().rstrip("\\n")')
  texts = texts.replace('C2L = HOME + "/ccg2lambda"', 'with open("../ccg2lambda_location.txt", "r") as f:\n\tC2L = f.read().rstrip("\\n")')
  texts = texts.replace('tpp9.theoremProve_prover9', 'tpp9.theoremProving')
  texts = texts.replace('theoremProve_Prover9', 'theoremProver_Prover9')

  with open(path, "w") as f:
    f.write(texts)
