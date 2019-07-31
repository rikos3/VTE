from nltk.sem.logic import *

lexpr = Expression.fromstring

compounds_2 = [('part', 'of'),
               ('next', 'to'),
               ('mute', 'swan'), 
               ("sit", "on"),
               ("sit", "in"),
               ("stand", "on"),
               ("stand", "in"),
               ("lie", "on"),
               ("lie", "in"),
               ("look", "at")]

compounds_3 = [("in", "front", "of")]

def split(expr, lst, variables):
  if isinstance(expr, ExistsExpression):
    var = expr.variable
    variables.insert(0, var)
    term = expr.term
    return (split(term, lst, variables))
  elif isinstance(expr, AndExpression):
    fst = expr.first
    snd = expr.second
    lst.append(snd)
    return (split(fst, lst, variables))
  else:
    lst.append(expr)
    return (lst, variables)

def split_app(expr, args):
  if isinstance(expr, ConstantExpression):
    return (expr, args)
  elif isinstance(expr, ApplicationExpression):
    f = expr.function
    arg = expr.argument
    args.insert(0, arg)
    return (split_app(f, args))
  else:
    return (expr, args)

def make_compound_2(lst):
  for word1, word2 in compounds_2:
    f1, args1, flag1 = '', [], 0
    f2, args2, flag2 = '', [], 0

    for i in range(len(lst)):
      f, args = split_app(lst[i], [])
      if str(f) == word1:
        flag1 = 1
        f1, args1 = f, args
        index1 = i
      elif str(f) == word2:
        flag2 = 1
        f2, args2 = f, args
        index2 = i

    if flag1 + flag2 == 2:
      if args1[0] == args2[0]:
        f = lexpr(word1 + '_' + word2)
        args = args2
        indexes = [index1, index2]
        del lst[max(indexes)]
        del lst[min(indexes)]
        lst.append(make_AppExpr(f, args))

  return (lst)

def make_compound_3(lst):
  for word1, word2, word3 in compounds_3:
    f1, args1, flag1 = '', [], 0
    f2, args2, flag2 = '', [], 0
    f3, args3, flag3 = '', [], 0
    for i in range(len(lst)):
      f, args = split_app(lst[i], [])
      if str(f) == word1:
        flag1 = 1
        f1, args1 = f, args
        index1 = i
      elif str(f) == word2:
        flag2 = 1
        f2, args2 = f, args
        index2 = i
      elif str(f) == word3:
        flag3 = 1
        f3, args3 = f, args
        index3 = i

    if flag1 + flag2 + flag3 == 3:
      if args1[1] == args3[0]:
        f = lexpr(word1 + '_' + word2 + '_' + word3)
        args = [args1[0], args3[1]]
        indexes = [index1, index2, index3]
        for n in range(len(indexes)):
          max_index = max(indexes)
          del lst[max_index]
          indexes.remove(max_index)
          lst.append(make_AppExpr(f, args))
  return (lst)

def make_AppExpr(f, args):
  if len(args) == 1:
    return (ApplicationExpression(f, args[0]))
  else:
    fst = args[0]
    rest = args[1:]
    fx = ApplicationExpression(f, fst)
    return (make_AppExpr(fx, rest))

def combine(expr, lst):
  if lst == []:
    return (expr)
  else:
    fst = lst[0]
    rest = lst[1:]
    expr2 = AndExpression(fst, expr)
    return (combine(expr2, rest))

def make_ExistsExpr(expr, variables):
  if variables == []:
    return (expr)
  else:
    var = variables[0]
    rest = variables[1:]
    expr2 = ExistsExpression(var, expr)
    return (make_ExistsExpr(expr2, rest))

# main
def make_compound(text):
  expr = lexpr(text)
  expr_lst, variables = split(expr, [], [])
  expr_lst3_2 = expr_lst
  while True:
    expr_lst3_1 = make_compound_3(expr_lst3_2)
    expr_lst3_2 = make_compound_3(expr_lst3_1)
    if expr_lst3_1 == expr_lst3_2:
      expr_lst3 = expr_lst3_1
      break
  expr_lst2_2 = expr_lst3
  while True:
    expr_lst2_1 = make_compound_2(expr_lst2_2)
    expr_lst2_2 = make_compound_2(expr_lst2_1)
    if expr_lst2_1 == expr_lst2_2:
      expr_lst = expr_lst2_1
      break
  fst = expr_lst[0]
  rest = expr_lst[1:]
  expr2 = combine(fst, rest)
  expr3 = make_ExistsExpr(expr2, variables)
  res = str(expr3)
  return (res)
