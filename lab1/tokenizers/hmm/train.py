# -*- coding: gbk -*-
import pickle
import re
from math import log
import tqdm

pre = {'B': 'ES', 'M': 'MB', 'S': 'SE', 'E': 'BM'}  # 标志可以出现在当前状态之前的状态
states = ['B', 'M', 'E', 'S']  # 状态集
date_pattern = '[0-9]*[-][0-9]*[-][0-9]{3}[-][0-9]{3}'


class train():
    """
    使用EM算法对HMM的参数进行训练
    """

    def __init__(self):
        self.pi = {}  # 初始状态集
        self.A = {}  # 状态转移概率
        self.B = {}  # 发射概率
        self.line_num = 0  # 统计句子数
        self.word_dic = set()  # 保存出现过的词
        self.state_num = {}  # 记录每一个状态出现的次数
        for state in states:
            self.state_num[state] = 0.0
            self.pi[state] = 0.0
            self.A[state] = {}
            self.B[state] = {}
            for temp_state in states:
                self.A[state][temp_state] = 0.0  # state->temp_state的转移概率初始化

    def write_res(self, save_model_path):
        """
        保存训练得到的参数
        :param save_model_path:保存地址
        :return:
        """
        with open(save_model_path, "wb") as f:
            pickle.dump(self.pi, f)
            pickle.dump(self.A, f)
            pickle.dump(self.B, f)
        f.close()

    def tag_line(self, line):
        """
        给一行文本标注，返回一行中每一个字对应的[B,M,E,S]
        :param line:需要标注的文本
        :return:标注结果
        """
        line_word = []
        line_tag = []
        for word in line.split():
            word = word[1 if word[0] == '[' else 0:word.index('/')]
            self.line_num += 1
            if len(word) == 0:
                continue
            if word[-1] == ']':
                word = word[0:-1]

            line_word.extend(list(word))
            self.word_dic.add(word)
            # 对句首状态进行记录
            if len(word) == 1:
                self.pi['S'] += 1
                line_tag.append('S')
            else:
                self.pi['B'] += 1
                self.pi['E'] += 1
                self.pi['M'] += len(word) - 2
                line_tag.append('B')
                line_tag.extend(['M'] * (len(word) - 2))
                line_tag.append('E')
        assert len(line_tag) == len(line_word)
        return line_word, line_tag

    def tag_text(self, res_path, train_file=None):

        if train_file is None:
            train_file = ['../../data/199801_seg&pos.txt', '../../data/199802.txt', '../../data/199803.txt',
                          '../../data/name_pre.txt']

        assert train_file is not None

        for file in train_file:
            with open(file, encoding='gbk', errors='ignore') as f:
                lines = f.readlines()
                for line in tqdm.tqdm(lines):
                    if line is None or line == '\n':
                        continue
                    line = re.sub(date_pattern, '', line)
                    word,tag = self.tag_line(line)
                    # print(word)
                    # print(tag)
                    for i in range(len(tag)):
                        self.state_num[tag[i]] += 1
                        self.B[tag[i]][word[i]] = self.B[tag[i]].get(word[i], 0) + 1  # 发射概率
                        # print(self.B[tag[i]].get(word[i], 0))
                        if i > 0:  # 转移概率
                            self.A[tag[i - 1]][tag[i]] += 1
                f.close()

        # 更新参数
        for state in states:
            a = 0.00001
            # 四种状态
            self.pi[state] = log((self.pi[state] + a) / (self.line_num + a * 4))
            for temp_state in states:
                self.A[state][temp_state] = log((self.A[state][temp_state] + a) / (self.state_num[state] + a * 4))
            for word in self.B[state].keys():
                self.B[state][word] = log((self.B[state][word] + a) / (self.state_num[state] + a * len(self.word_dic)))
        self.write_res(res_path)


if __name__ == '__main__':
    h1 = train()
    h1.tag_text('../../data/h.pkl')
    print(h1.pi)
    print(h1.A)
    print(h1.B)
