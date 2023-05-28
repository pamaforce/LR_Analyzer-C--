import copy
import os.path
import re

'''
关键字、运算符和分隔符
kw = ['int', 'void', 'return', 'const']
op = ['+', '-', '*', '/', '%', '=', '>', '<', '==', '<=', '>=', '!=', '&&', '||']
se = ['(', ')', '{','}',';',',']
'''

# 定义字符集
type_char = ['A', 'B', 'C', 'D', 'E']
'''
A: 表示任意字符，即包括字母、数字和其他字符。
B: 表示所有数字。
C: 表示非零数字，即数字1到9。
D: 表示标识符的第一个字符，包括大写字母、小写字母和下划线。
E: 表示标识符的其他字符，包括大写字母、小写字母、数字和下划线。
'''

EPSILON = 'ε'

number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

capital_letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                  'W', 'X', 'Y', 'Z']

lowercase_letter = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
                    'w', 'x', 'y', 'z']

symbols = ['=', '>', '<', '/', '*', '|', '&', '_', ' ',
           ';', '{', '}', '%', '!', '+', '-', '.', ',', '(', ')']

all_char = capital_letter + lowercase_letter + \
    number + symbols + type_char + ['"']

# 配置文件解析类


class MyConfigParser:
    def __init__(self, path, cut='~'):
        config_path = './config'
        self.list = []  # 存储解析后的配置项列表
        self.cut = cut  # 分隔符，默认为"~"
        type_name = 'DEFAULT'  # 默认的节名为"DEFAULT"
        with open(config_path, 'r') as reader:  # 打开配置文件进行读取
            for line in reader.readlines():  # 逐行读取配置文件内容
                line = line.strip('\n')  # 去除行末的换行符
                if line == '':  # 如果是空行，则跳过
                    continue
                if line[0] == '<' and line[-1] == '>':  # 如果行以方括号包围，则表示为节名
                    type_name = line[1:-1]  # 获取节名（去除方括号）
                else:
                    # 将"IDN_START"替换为"$(D$)"
                    line = re.sub('IDN_START', '$(D$)', line)
                    # 将"IDN_OTHER"替换为"$(E$)"
                    line = re.sub('IDN_OTHER', '$(E$)', line)
                    # 将"NUMS_NOT_ZERO"替换为"$(C$)"
                    line = re.sub('NUMS_NOT_ZERO', '$(C$)', line)
                    # 将"ALL_NUMS"替换为"$(B$)"
                    line = re.sub('ALL_NUMS', '$(B$)', line)
                    token, reg, num = line.split(
                        self.cut)  # 使用分隔符切分行，得到类型名、正则表达式和序号
                    if type_name == 'VALUE':  # 如果节名为"VALUE"
                        # 构造元组，包含节名、配置项、正则表达式和序号
                        t = (type_name, token, reg, num)
                        self.list.append(t)  # 将元组添加到配置项列表中
                        pass
                    else:
                        # 构造元组，包含节名、配置项、正则表达式和序号
                        t = (type_name, token, reg, num)
                        self.list.append(t)  # 将元组添加到配置项列表中
            pass


# NFA状态索引
NFACount = 0

# 表示DFA状态，包含NFA节点列表、NFA节点的索引列表和是否是终止状态的标志


class DState:
    def __init__(self, ListNFA, final=False, FinHash=None):
        self.NFANum = []  # 存储NFA节点的索引列表
        self.final = final  # 表示当前状态是否为终止状态，默认为False
        self.value = None  # 当前状态对应的值，默认为None
        self.NFANode = ListNFA  # 存储NFA节点列表
        if FinHash is None:
            FinHash = []  # 如果FinHash参数为None，则将其设置为空列表
        for node in self.NFANode:  # 遍历NFA节点列表
            if node.index in FinHash:  # 如果节点的索引在FinHash中
                self.value = node.value  # 设置当前状态的值为节点的值
            self.NFANum.append(node.index)  # 将节点的索引添加到NFANum列表中

    def __hash__(self):
        tabul = []
        for node in self.NFANode:  # 遍历NFA节点列表
            tabul.append(str(node.index))  # 将节点的索引转换为字符串并添加到tabul列表中
        tabul.sort()  # 对tabul列表进行排序
        s = ' '.join(tabul)  # 将tabul列表中的元素用空格连接成字符串
        return hash(s)  # 返回字符串的哈希值

    def __eq__(self, other):
        if isinstance(other, DState):  # 判断other是否为DState的实例
            return hash(other) == self.__hash__()  # 比较当前状态的哈希值与other的哈希值是否相等
        else:
            return False  # 若other不是DState的实例，则返回False

    def __ne__(self, other):
        return not self.__eq__(other)  # 返回当前状态与other是否不相等的结果

    def __str__(self):
        tabul = []
        for node in self.NFANode:  # 遍历NFA节点列表
            tabul.append(str(node.index))  # 将节点的索引转换为字符串并添加到tabul列表中
        tabul.sort()  # 对tabul列表进行排序
        s = ' '.join(tabul)  # 将tabul列表中的元素用空格连接成字符串
        return s  # 返回表示该状态的字符串

# 最小化DFA


def GetMinDFA(converse_table, initial_node):
    return converse_table, initial_node  # 返回输入的converse_table和initial_node，不进行任何操作

# 表示NFA结构，包含起始节点、终止节点和边列表


class NFAStruct:
    def __init__(self, startNode=None, endNode=None, edges=None):
        self.edges = edges  # 边列表
        self.startNode = startNode  # 起始节点
        self.endNode = endNode  # 终止节点
        if edges is None:
            edges = []  # 如果edges参数为None，则将其设置为空列表

# 表示NFA节点，包含是否是终止状态的标志、节点索引、入边列表和出边列表


class NFANode:
    def __init__(self, value=None, is_final=False):
        self.is_final = is_final  # 是否是终止状态的标志，默认为False
        global NFACount
        NFACount += 1
        self.index = NFACount - 1  # 节点索引，使用全局变量NFACount自增生成
        self.content = value  # 节点的内容（值）
        self.InEdge = []  # 入边列表
        self.OutEdge = []  # 出边列表

    def __str__(self):
        return str(self.index)  # 返回节点的索引的字符串表示形式

# 表示NFA边，包含起始节点、结束节点和边上的符号


class NFAEdge:
    def __init__(self, start: NFANode, end: NFANode, symbol: str):
        self.symbol = symbol  # 边上的符号
        self.start = start  # 起始节点
        self.end = end  # 结束节点
        self.connectBi()  # 连接起始节点和结束节点的双向关系

    def __str__(self):
        return self.symbol  # 返回边上的符号的字符串表示形式

    def connectBi(self):
        self.start.OutEdge.append(self)  # 将边添加到起始节点的出边列表中
        self.end.InEdge.append(self)  # 将边添加到结束节点的入边列表中

# 计算给定节点集合的ε闭包


def epsilon_closure(input, endNodes):
    endNodesHash = list(map(lambda x: x.index, endNodes))  # 将终止节点集合转换为索引列表
    global EPSILON  # 全局变量EPSILON表示ε符号
    flag = False  # 终止状态标志，默认为False
    if type(input) == list:  # 如果输入是列表类型（节点集合）
        result_set = copy.deepcopy(input)  # 创建节点集合的深拷贝
        stack = copy.deepcopy(input)  # 创建节点集合的深拷贝作为栈
        while len(stack) != 0:  # 当栈不为空时循环
            ele = stack.pop()  # 弹出栈顶元素
            if ele.index in endNodesHash:  # 如果栈顶元素是终止节点之一
                flag = True  # 设置终止状态标志为True
            for edge in ele.OutEdge:  # 遍历栈顶元素的出边
                # 如果出边的符号是ε且结束节点不在结果集中
                if edge.symbol == EPSILON and (edge.end not in result_set):
                    result_set.append(edge.end)  # 将结束节点添加到结果集中
                    stack.append(edge.end)  # 将结束节点压入栈中
        # 返回生成的DState对象，包含结果集、终止状态标志和终止节点索引列表
        return DState(result_set, flag, endNodesHash)
    else:  # 如果输入不是列表类型（单个节点）
        result_set = [copy.deepcopy(input)]  # 创建包含输入节点的结果集
        stack = [copy.deepcopy(input)]  # 创建包含输入节点的栈
        while len(stack) != 0:  # 当栈不为空时循环
            ele = stack.pop()  # 弹出栈顶元素
            if ele.index in endNodesHash:  # 如果栈顶元素是终止节点之一
                flag = True  # 设置终止状态标志为True
            for edge in ele.OutEdge:  # 遍历栈顶元素的出边
                # 如果出边的符号是ε且结束节点不在结果集中
                if edge.symbol == EPSILON and (edge.end not in result_set):
                    result_set.append(edge.end)  # 将结束节点添加到结果集中
                    stack.append(edge.end)  # 将结束节点压入栈中
        # 返回生成的DState对象，包含结果集、终止状态标志和终止节点索引列表
        return DState(result_set, flag, endNodesHash)


# 根据给定节点集合和输入字符生成下一个节点集合
def cal_nxt(now: DState, sheet, all_D, endNodes):
    for char in all_char:  # 遍历所有字母（输入字符）
        temp_list = []  # 临时列表，用于存储符合条件的节点
        for node in now.NFANode:  # 遍历给定节点集合中的节点
            for edge in node.OutEdge:  # 遍历节点的出边
                if edge.symbol == char:  # 如果出边的符号与输入字符相等
                    temp_list.append(edge.end)  # 将出边的结束节点添加到临时列表中
        if len(temp_list) == 0:  # 如果临时列表为空，说明没有符合条件的节点
            continue  # 继续下一次循环，处理下一个输入字符
        nxt = epsilon_closure(temp_list, endNodes)  # 根据临时列表和终止节点集合计算下一个节点集合nxt
        if nxt not in all_D:  # 如果下一个节点集合nxt不在已有的节点集合集合中
            all_D.add(nxt)  # 将nxt添加到节点集合集合中
            sheet[nxt] = {}  # 在转换表中为nxt创建一个空字典
        if now not in sheet.keys():  # 如果当前节点集合now不在转换表的键中
            sheet[now] = {}  # 在转换表中为now创建一个空字典
            sheet[now][char] = nxt  # 将now和输入字符char的转换结果指向nxt
        else:
            sheet[now][char] = nxt  # 将now和输入字符char的转换结果指向nxt
    pass


# 根据NFA结构生成DFA
def cal_DFA(DS: NFAStruct):
    all_D = set()  # 存储所有生成的DState集合
    sign_D = set()  # 存储已经处理过的DState集合
    converse_table = {}  # 存储生成的DFA的转换表
    initial_node = epsilon_closure(
        DS.startNode, DS.endNode)  # 计算起始节点的ε闭包作为初始节点集合
    all_D.add(initial_node)  # 将初始节点集合加入所有DState集合中
    while len(all_D - sign_D) != 0:  # 当还有未处理的DState集合时
        now = (all_D - sign_D).pop()  # 从未处理的DState集合中取出一个DState
        sign_D.add(now)  # 将该DState加入已处理的DState集合中
        # 根据当前DState生成下一个节点集合，并更新转换表converse_table和所有DState集合all_D
        cal_nxt(now, converse_table, all_D, DS.endNode)
    converse_table, initial_node = GetMinDFA(
        converse_table, initial_node)  # 最小化DFA，得到最终的转换表和起始节点集合
    return converse_table, initial_node


REG_OPS = ['$(', '$|', '$*', '$+']

# 根据配置文件中的正则表达式生成NFA


def cal_NFA():
    config = MyConfigParser('./Lexical/config')  # 解析配置文件
    DFAs = []  # 存储生成的NFA列表
    for (type_name, token, reg, num) in config.list:  # 遍历配置文件中的每个正则表达式
        ans = dijkstra(reg)  # 根据正则表达式生成NFA
        ans.endNode.value = (type_name, token, reg, num)  # 设置NFA的终止节点的值
        DFAs.append(ans)  # 将生成的NFA添加到NFA列表中
    all_start = NFANode()  # 创建一个新的起始节点
    complete_NFA = NFAStruct(all_start, [], [])  # 创建完整的NFA结构对象
    for sct in DFAs:  # 遍历NFA列表中的每个NFA
        # 创建一个连接起始节点和NFA起始节点的ε边
        edge = NFAEdge(all_start, sct.startNode, EPSILON)
        complete_NFA.edges.append(edge)  # 将连接起始节点和NFA起始节点的ε边添加到完整NFA的边列表中
        complete_NFA.edges += sct.edges  # 将NFA的边列表添加到完整NFA的边列表中
        complete_NFA.endNode.append(sct.endNode)  # 将NFA的终止节点添加到完整NFA的终止节点列表中
    return complete_NFA  # 返回完整的NFA结构


# 将正则表达式转换为NFA
def dijkstra(input):
    ops = []  # 运算符栈
    vals = []  # 值栈
    skip_mode = False  # 跳过模式标志
    input = '$(' + input + '$)'  # 在正则表达式前后添加特殊符号$，表示起始和结束
    input = input.replace('$)$(', '$)$+$(')  # 将$)$替换为$)$+$(
    for index, char in enumerate(input):
        if skip_mode:
            skip_mode = False
            continue
        if char == '$':
            char += input[index + 1]  # 将$和后一个字符合并成一个字符
            skip_mode = True
        if char in REG_OPS:  # 如果是正则表达式的运算符
            ops.append(char)  # 将运算符入栈
        elif char == '$)':  # 如果是$)
            top_op = ops.pop()  # 弹出栈顶运算符
            while len(ops) != 0 and top_op != '$(':  # 当运算符栈非空且栈顶运算符不是$(
                if top_op == '$|':  # 如果是$|
                    start = NFANode()  # 创建起始节点
                    end = NFANode()  # 创建终止节点
                    prev_val = vals.pop()  # 弹出前一个值
                    next_val = vals.pop()  # 弹出后一个值
                    edge1 = NFAEdge(start, prev_val.startNode,
                                    EPSILON)  # 创建连接起始节点和前一个值起始节点的ε边
                    edge2 = NFAEdge(start, next_val.startNode,
                                    EPSILON)  # 创建连接起始节点和后一个值起始节点的ε边
                    # 创建连接前一个值终止节点和终止节点的ε边
                    edge3 = NFAEdge(prev_val.endNode, end, EPSILON)
                    # 创建连接后一个值终止节点和终止节点的ε边
                    edge4 = NFAEdge(next_val.endNode, end, EPSILON)
                    vals.append(NFAStruct(start, end, [
                                edge1, edge2, edge3, edge4] + prev_val.edges + next_val.edges))  # 将生成的NFAStruct压入值栈
                    del prev_val
                    del next_val
                elif top_op == '$+':  # 如果是$+
                    next_val = vals.pop()  # 弹出后一个值
                    prev_val = vals.pop()  # 弹出前一个值
                    first_end = prev_val.endNode  # 前一个值的终止节点
                    second_start = next_val.startNode  # 后一个值的起始节点
                    for edge in prev_val.edges:
                        if edge.end == first_end:
                            edge.end = second_start  # 将连接前一个值终止节点的边的结束节点改为后一个值起始节点
                    vals.append(NFAStruct(prev_val.startNode, next_val.endNode,
                                prev_val.edges + next_val.edges))  # 将生成的NFAStruct压入值栈
                elif top_op == '$*':  # 如果是$*
                    val = vals.pop()  # 弹出值
                    start = NFANode()  # 创建起始节点
                    end = NFANode()  # 创建终止节点
                    edge1 = NFAEdge(start, end, EPSILON)  # 创建连接起始节点和终止节点的ε边
                    # 创建连接起始节点和值起始节点的ε边
                    edge2 = NFAEdge(start, val.startNode, EPSILON)
                    # 创建连接值终止节点和终止节点的ε边
                    edge3 = NFAEdge(val.endNode, end, EPSILON)
                    edge4 = NFAEdge(val.endNode, val.startNode,
                                    EPSILON)  # 创建连接值终止节点和值起始节点的ε边
                    # 将生成的NFAStruct压入值栈
                    vals.append(
                        NFAStruct(start, end, [edge1, edge2, edge3, edge4] + val.edges))
                top_op = ops.pop()  # 弹出栈顶运算符
            pass
        else:  # 如果是普通字符
            if input[index - 2:index] not in REG_OPS:  # 如果前两个字符不是正则表达式的运算符
                ops.append('$+')  # 将$+入栈
            start = NFANode()  # 创建起始节点
            end = NFANode()  # 创建终止节点
            edge = NFAEdge(start, end, char)  # 创建连接起始节点和终止节点的边
            s = NFAStruct(start, end, [edge])  # 创建包含边的NFAStruct
            vals.append(s)  # 将NFAStruct压入值栈
    return vals[0]  # 返回值栈中的第一个值


class Scanner:
    def __init__(self):
        self.NFA = cal_NFA()  # 生成NFA
        self.converse_table, self.initial_node = cal_DFA(self.NFA)  # 生成DFA

    def scan(self, path, out_path):
        if os.path.exists(path):
            f = open(path, 'r')
            total = f.read().strip('\t')
            total = ' ' + total
            total = total.replace('\t', ' ')
            total = total.replace('\n', ' ')
            total = total.replace('\r', ' ')
            total = re.sub(' +', ' ', total)
            p = 0
            late_pointer = 0
            token_list = []
            char = ' '
            value_start_pointer = 0
            check_point_token = None
            this_state = self.initial_node
            while p <= len(total):
                if p < len(total):
                    char = total[p]
                char, flag = self.isLegal(
                    char, self.converse_table[this_state].keys())  # 判断字符是否在DFA的转换表中
                if flag and p != len(total):
                    # 获取下一个状态
                    next_state = self.converse_table[this_state][char]
                    if next_state.final:
                        check_point_token = next_state
                        late_pointer = p
                    this_state = next_state
                else:
                    if check_point_token is not None:
                        if check_point_token.value[0] != 'SPACE':
                            token_list.append(
                                check_point_token.value + tuple([total[value_start_pointer + 1:late_pointer + 1]]))  # 将识别到的token添加到列表中
                        check_point_token = None
                        value_start_pointer = late_pointer
                        p = late_pointer
                        this_state = self.initial_node
                        if p == len(total) - 1:
                            break
                    else:
                        raise Exception(
                            "Unrecognized character, occurred in the %sth character." % (str(p)))
                p += 1
            # 输出识别到的token到文件并返回token列表
            return self.output(token_list, out_path)
            f.close()
        else:
            raise Exception('File does not exist.')  # 抛出异常，表示文件不存在

    def output(self, list, out_path):
        token_list = []
        with open(out_path, 'w', newline='') as f:
            for item in list:
                type_name, token, reg, num, value = item
                token_list.append(token)
                if type_name == 'VALUE':
                    f.write("%s\t<%s>\n" % (value, token))
                else:
                    f.write("%s\t<%s>\n" % (token, type_name))
        return token_list

    def isLegal(self, char, keys):
        flag = False
        if char in keys:
            flag = True
        elif 'A' in keys and char in capital_letter + lowercase_letter + number + symbols:
            # all
            char = 'A'
            flag = True
        elif 'B' in keys and char in number:
            # 所有数字
            char = 'B'
            flag = True
        elif 'C' in keys and char in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            # 非0数字
            char = 'C'
            flag = True
        elif 'D' in keys and char in capital_letter + lowercase_letter + ['_']:
            # 标识符第一个字符
            char = 'D'
            flag = True
        elif 'E' in keys and char in capital_letter + lowercase_letter + number + ['_']:
            # 标识符其它字符
            char = 'E'
            flag = True
        return char, flag


if __name__ == '__main__':
    scanner = Scanner()
    token_list = scanner.scan('./test.txt', './lex.txt')
