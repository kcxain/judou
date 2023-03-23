# -*- coding: gbk -*-
import pickle
import re
from math import log
import tqdm

from .mm import write_file
from .utils import begging_number

# 最小值
MIN_FLOAT = -3.14e100
pre = {'B': 'ES', 'M': 'MB', 'S': 'SE', 'E': 'BM'}  # 标志可以出现在当前状态之前的状态
states = ['B', 'M', 'E', 'S']  # 状态集
date_pattern = '[0-9]*[-][0-9]*[-][0-9]{3}[-][0-9]{3}'


class model:
    def __init__(self, model_path='../../data/hmm_model/hmm_model.pkl'):
        """
        初始化
        :param model_path: 模型参数存储地址
        """
        # 初始状态分布
        self.pi = {}
        # 状态转移矩阵
        self.A = {}
        # 发射矩阵
        self.B = {}
        # 加载参数
        self.load_model(model_path)

    def viterbi(self, text):
        """
        viterbi算法
        :param text: 输入的文本
        :return: 标注
        """
        V = [{}]
        path = {}
        # 所有可能的下一步状态
        for y in states:
            V[0][y] = self.pi[y] + self.B[y].get(text[0], MIN_FLOAT)
            path[y] = [y]
        for t in range(1, len(text)):
            V.append({})
            newpath = {}
            for y in states:
                em_p = self.B[y].get(text[t], MIN_FLOAT)
                (prob, state) = max(
                    [(V[t - 1][y0] + self.A[y0].get(y, MIN_FLOAT) + em_p, y0) for y0 in pre[y]])
                V[t][y] = prob
                # 上一刻最优状态+这一时刻状态
                newpath[y] = path[state] + [y]
            path = newpath

        (prob, state) = max((V[len(text) - 1][y], y) for y in 'ES')

        return prob, path[state]

    def merge(self, words):
        """
        处理单词串
        :param words: 单字列表
        :return: 分词结果
        """
        if len(words) == 1:
            return words
        seg_list = self.viterbi(words)[1]
        res = ''
        for i in range(len(words)):
            tag = seg_list[i]
            if tag == 'B' or tag == 'M':
                res += words[i]
            elif tag == 'E' or tag == 'S':
                res += words[i] + '/'
        res = res.rstrip()
        res = res.split('/')[0:-1]
        return res

    def line_seg(self, word_list):
        """
        对分词结果的中的单字进行合并
        :param word_list: 分词结果
        :return: 合并后的分词结果
        """
        sentence_seg = []
        i = 0
        while i < len(word_list):
            tmp = []
            j = i
            while j < len(word_list) and len(word_list[j]) == 1 and word_list[j]:
                tmp.append(word_list[j])
                j += 1
            if len(tmp) > 0:
                sentence_seg.extend(self.merge(tmp))
            tmp.clear()
            i = j
            if i < len(word_list):
                sentence_seg.append(word_list[i])
            i += 1
        return sentence_seg

    def cut_sentence(self, sentence):
        """
        抄的jieba的代码，写的比较优雅
        :param sentence:
        :return:
        """
        global emit_P
        prob, pos_list = self.viterbi(sentence)
        begin, nexti = 0, 0
        # print pos_list, sentence
        for i, char in enumerate(sentence):
            pos = pos_list[i]
            if pos == 'B':
                begin = i
            elif pos == 'E':
                yield sentence[begin:i + 1]
                nexti = i + 1
            elif pos == 'S':
                yield char
                nexti = i + 1
        if nexti < len(sentence):
            yield sentence[nexti:]

    def tokenizer(self, data_file='../../data/origin_data_set/199801_sent.txt',
                  target_file='../../data/test_output/seg_HMM.txt'):
        """
        使用HMM对文本进行分词
        :param target_file: 欲分词文本
        :param data_file: 输出
        :param text_path: 需要分词的文本所在地址
        :param io_path:分词结果输出地址
        :return:
        """
        with open(data_file, encoding='gbk') as f:
            lines = f.readlines()
            tf = open(target_file, 'w')
            # f_words = []
            for line in tqdm.tqdm(lines):
                segList = []
                line = begging_number(line, segList)
                list_iter = self.cut_sentence(line)
                for i in list_iter:
                    segList.append(i)
                # print(segList)
                # print(f_words)
                write_file(segList, tf)
            f.close()
            tf.close()

    def load_model(self, model_path):
        """
        加载模型，初始化各个参数矩阵
        :param model_path: 模型地址
        :return:
        """
        with open(model_path, "rb") as f:
            self.pi = pickle.load(f)
            self.A = pickle.load(f)
            self.B = pickle.load(f)
        f.close()


class train():
    """
    训练HMM参数
    """

    def __init__(self, model_path):
        # 初始状态分布
        self.pi = {}
        # 状态转移矩阵
        self.A = {}
        # 发射矩阵
        self.B = {}
        self.num = 0
        self.words = set()
        # 每种状态的数目
        self.state_num = {}
        # 模型保存地址
        self.model_path = model_path
        # 全部初始化为0
        for state in states:
            self.state_num[state] = 0.0
            self.pi[state] = 0.0
            self.A[state] = {}
            self.B[state] = {}
            for temp_state in states:
                self.A[state][temp_state] = 0.0

    def tag(self, line):
        """
        标注文本的由字构词
        :param line: 待标记文本
        :return: tag
        """
        line_word = []
        line_tag = []
        for word in line.split():
            word = word[1 if word[0] == '[' else 0:word.index('/')]
            self.num += 1
            if len(word) == 0:
                continue
            if word[-1] == ']':
                word = word[0:-1]

            line_word.extend(list(word))
            self.words.add(word)
            # 单字
            if len(word) == 1:
                self.pi['S'] += 1
                line_tag.append('S')
            else:
                self.pi['B'] += 1
                # 初始状态只能是B和S
                # self.pi['E'] += 1
                # self.pi['M'] += len(word) - 2
                line_tag.append('B')
                line_tag.extend(['M'] * (len(word) - 2))
                line_tag.append('E')
        assert len(line_tag) == len(line_word)
        return line_word, line_tag

    def train_text(self, train_file=None):

        if train_file is None:
            train_file = ['../../data/origin_data_set/199801_seg&pos.txt', '../../data/origin_data_set/199802.txt',
                          '../../data/origin_data_set/199803.txt',
                          '../../data/origin_data_set/name_pre.txt']

        assert train_file is not None

        for file in train_file:
            with open(file, encoding='gbk', errors='ignore') as f:
                lines = f.readlines()
                for line in tqdm.tqdm(lines):
                    if line is None or line == '\n':
                        continue
                    line = re.sub(date_pattern, '', line)
                    word, tag = self.tag(line)
                    # print(word)
                    # print(tag)
                    for i in range(len(tag)):
                        self.state_num[tag[i]] += 1
                        self.B[tag[i]][word[i]] = self.B[tag[i]].get(word[i], 0) + 1
                        if i > 0:
                            self.A[tag[i - 1]][tag[i]] += 1
                f.close()
        self.update_model()

    def save_model(self):
        """
        保存HMM训练参数
        :return:
        """
        with open(self.model_path, "wb") as f:
            pickle.dump(self.pi, f)
            pickle.dump(self.A, f)
            pickle.dump(self.B, f)
        f.close()

    def update_model(self):
        """
        重新计算概率矩阵
        :return:
        """
        for state in states:
            a = 0.00001
            # 四种状态
            self.pi[state] = MIN_FLOAT if self.pi[state] == 0 else log((self.pi[state]) / self.num)
            for temp_state in states:
                self.A[state][temp_state] = MIN_FLOAT if self.A[state][temp_state] == 0 else log(
                    (self.A[state][temp_state]) / (self.state_num[state]))
            for word in self.B[state].keys():
                self.B[state][word] = MIN_FLOAT if self.B[state][word] == 0 else log(
                    (self.B[state][word]) / (self.state_num[state]))
