import csv
from collections import deque

import pandas as pd

i = 1  # 产生式的行序号
grammar = [("S'", ['program'])]  # 用来存储所有文法
grammar_dict = {}  # 以非终结符为索引存储产生式
symbols = set(['program'])  # 用来存所有符号
nonterminal_symbols = set()  # 用来存所有非终结符
terminal_symbols = set()  # 用来存所有终结符

with open('grammar.txt', 'r') as file:
    grammar_lines = file.readlines()

# 解析语法规则并保存到变量中，并同时存储终结符和非终结符
for line in grammar_lines:
    nonterminal, productions = line.strip('\n').split(' -> ')
    productions = productions.split(' ')  # 产生式列表
    nonterminal_symbols.add(nonterminal)
    if nonterminal not in grammar_dict:
        grammar_dict[nonterminal] = []
    if productions[0] == '$':  # 将$变为空储存
        grammar.append((nonterminal, []))
    else:
        grammar.append((nonterminal, productions))
        symbols.update(productions)
    grammar_dict[nonterminal].append(i)
    i += 1
terminal_symbols = symbols - nonterminal_symbols  # 求出终结符
terminal_symbols.add('$')

# 计算FIRST集
FIRST = {}
for nonterminal in grammar_dict:
    FIRST[nonterminal] = []
flag = True  # 用来标志FIRST集是否改变
while flag:
    flag = False
    for nonterminal in grammar_dict:
        for line_id in grammar_dict[nonterminal]:
            productions = grammar[line_id][1]
            max_non = 0
            if not productions:
                if '$' not in FIRST[nonterminal]:
                    FIRST[nonterminal].append('$')
                    flag = True
                continue
            for index in range(len(productions)):
                if productions[index] in terminal_symbols:
                    if productions[index] not in FIRST[nonterminal]:
                        FIRST[nonterminal].append(productions[index])
                        flag = True
                    max_non = index
                    break
                if '$' not in FIRST[productions[index]]:
                    max_non = index + 1
                    break
                if index == len(productions) - 1:
                    if '$' not in FIRST[nonterminal]:
                        FIRST[nonterminal].append('$')
                        flag = True
                    max_non = len(productions)
            for index in range(max_non):
                for char in FIRST[productions[index]]:
                    if char not in FIRST[nonterminal] and char != '$':
                        FIRST[nonterminal].append(char)
                        flag = True

# 计算FOLLOW集
FOLLOW = {}
for non_terminal in grammar_dict:
    FOLLOW[non_terminal] = []
FOLLOW['program'].append('#')
flag = True  # 用来标志FOLLOW集是否改变
while flag:
    flag = False
    for non_terminal in grammar_dict:
        for line_id in grammar_dict[non_terminal]:
            productions = grammar[line_id][1]
            for index in range(len(productions)):
                if productions[index] not in terminal_symbols:
                    first = []
                    max_non = index + 1
                    for i in range(index + 1, len(productions)):
                        if productions[i] in terminal_symbols:
                            if productions[i] not in first:
                                first.append(productions[i])
                            max_non = i
                            break
                        if '$' not in FIRST[productions[i]]:
                            max_non = i + 1
                            break
                        if i == len(productions) - 1:
                            max_non = len(productions)
                            if '$' not in first:
                                first.append('$')
                    for i in range(index + 1, max_non):
                        for char in FIRST[productions[i]]:
                            if char not in first and char != '$':
                                first.append(char)
                    for char in first:
                        if char not in FOLLOW[productions[index]] and char != '$':
                            FOLLOW[productions[index]].append(char)
                            flag = True
                    if index == len(productions) - 1 or '$' in first:
                        for char in FOLLOW[non_terminal]:
                            if char not in FOLLOW[productions[index]]:
                                FOLLOW[productions[index]].append(char)
                                flag = True


# 定义求闭包的函数，方便复用
def closure(_set):
    _list = list(_set)
    for item in _list:
        if item[1] < len(grammar[item[0]][1]) and grammar[item[0]][1][item[1]] in nonterminal_symbols:
            for i in grammar_dict[grammar[item[0]][1][item[1]]]:
                new_item = (i, 0)
                if new_item not in _set:
                    _list.append(new_item)
                    _set.add(new_item)
    return _set


# 求项目集规范族，并填充SLR表的GOTO部分
COLLECTION = [closure({(0, 0)})]
GOTO = []
for i, _set in enumerate(COLLECTION):
    GOTO.append(dict())
    for char in symbols:
        # 转换函数GO
        temp_set = set()
        for item in _set:
            if item[1] < len(grammar[item[0]][1]) and grammar[item[0]][1][item[1]] == char:
                temp_set.add((item[0], item[1] + 1))
        new_set = closure(temp_set)
        if len(new_set):
            if COLLECTION.count(new_set):
                GOTO[i][char] = COLLECTION.index(new_set)
            else:
                COLLECTION.append(new_set)
                GOTO[i][char] = len(COLLECTION) - 1

# 构造SLR分析表的ACTION部分
terminal_symbols.add('#')
terminal_symbols.remove('$')
columns = list(terminal_symbols) + list(nonterminal_symbols)
table = pd.DataFrame(data=' ', index=range(len(COLLECTION)), columns=columns)
for i, _set in enumerate(COLLECTION):
    for item in _set:
        if item == (0, 1):
            table.loc[i, '#'] = 'acc'
        elif item[1] < len(grammar[item[0]][1]):
            char = grammar[item[0]][1][item[1]]
            if char in terminal_symbols:
                table.loc[i, char] = 's' + str(GOTO[i][char])
            else:
                table.loc[i, char] = str(GOTO[i][char])
        elif item[1] == len(grammar[item[0]][1]):
            for char in terminal_symbols:
                if char in FOLLOW[grammar[item[0]][0]]:
                    table.loc[i, char] = 'r' + str(item[0])
terminal_symbols.remove('#')
terminal_symbols.add('$')

# 读取词法分析器输出的token流并处理后存到变量中
tokens = []
with open('lex.txt', 'r') as file:
    token_lines = file.readlines()

for line in token_lines:
    word, type = line.strip('\n').split('\t')
    if type == '<IDN>':
        tokens.append('IDN')
    elif type == '<INT>':
        tokens.append('INT')
    else:
        tokens.append(word)

# 移进归约过程并将中间结果按格式输出到gra.txt文件中
status_stack = deque([0])
symbol_stack = deque([])
input_list = deque(tokens)
step = 1
with open('gra.txt', 'w', newline='') as f:
    tsv_w = csv.writer(f, delimiter='\t')
    while True:
        status = status_stack[-1]
        symbol = input_list[0] if input_list else '#'
        top = symbol_stack[-1] if symbol_stack else 'EOF'
        if table.loc[status, symbol] == 'acc':
            tsv_w.writerow([step,  f'{top}#{symbol}', 'accept'])
            break
        elif table.loc[status, symbol] == ' ':
            tsv_w.writerow(
                [step, f'{top}#{symbol}', 'error'])
            break
        elif table.loc[status, symbol][0] == 's':
            status_stack.append(
                int(table.loc[status, symbol][1:]))
            symbol_stack.append(symbol)
            input_list.popleft()
            tsv_w.writerow([step,  f'{top}#{symbol}', 'move'])
        elif table.loc[status, symbol][0] == 'r':
            rule_num = int(table.loc[status, symbol][1:])
            left, right = grammar[rule_num]
            for _ in range(len(right)):
                status_stack.pop()
                symbol_stack.pop()
            status_stack.append(
                int(table.loc[status_stack[-1], left]))
            symbol_stack.append(left)
            tsv_w.writerow(
                [step, f'{top}#{symbol}', 'reduction'])
        else:
            tsv_w.writerow(
                [step, f'{top}#{symbol}', 'error'])
            break
        step += 1
