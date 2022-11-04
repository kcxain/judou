#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/11/30 21:48
# @Author  : ZSH
"""
本文件用于HMM分词
"""
import pickle
import tqdm
from lab1.tokenizers.oov.utils import begging_number
from lab1.tokenizers.fmm_bmm.MM import write_file

MIN = -10e+100  # 标志一个最小值
pre = {'B': 'ES', 'M': 'MB', 'S': 'SE', 'E': 'BM'}  # 标志可以出现在当前状态之前的状态
states = ['B', 'M', 'E', 'S']  # 状态集


class HMM:
    def __init__(self, model_path='../../data/h.pkl'):
        """
        初始化
        :param model_path: 模型参数存储地址
        """
        self.pi = {}  # 初始状态集
        self.A = {}  # 状态转移概率
        self.B = {}  # 发射概率

        with open(model_path, "rb") as f:
            self.pi = pickle.load(f)
            self.A = pickle.load(f)
            self.B = pickle.load(f)
        f.close()

    def viterbi(self, text):
        """
        viterbi算法，为text标注BEMS
        :param text:输入的文本
        :return:输出带标注的文本
        """
        path = {}  # 存储路径
        W = [{}]  # 存储到达每一个位置的时候的最优选择及其对应的值
        for state in states:
            W[0][state] = self.pi[state] + self.B[state].get(text[0], MIN)
            path[state] = [state]
        for i in range(1, len(text)):
            W.append({})
            temp_path = {}
            for state in states:
                emit = self.B[state].get(text[i], MIN)
                cost = MIN
                cur_state = 'S'
                for s in pre[state]:
                    temp = W[i - 1][s] + emit + self.A[s].get(state, MIN)
                    if temp > cost:
                        cost = temp
                        cur_state = s
                temp_path[state] = path[cur_state] + [state]
                W[i][state] = cost
            path = temp_path
        (cost, state) = max([(W[len(text) - 1][state], state) for state in 'ES'])  # 只有E和S有可能出现在末尾
        # print(path)
        return cost, path[state]

    def word_seg(self, words):
        """
        处理连续输入的单字的分词，例如输入[w1,w2,w3]，输出[w1,w2w3]
        :param words:需要处理的单字
        :return:分词结果
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
        对已经处理过的句子进行分词，句子形如[w1,w2,w3w4w5]
        :param word_list: 需要进一步分词的句子
        :param sentence_seg: 分词结果
        :return:分词结果
        """
        sentence_seg = []
        i = 0
        while i < len(word_list):
            tmp = []
            j = i
            while j < len(word_list) and len(word_list[j]) == 1:
                tmp.append(word_list[j])
                j += 1
            if len(tmp) > 0:
                sentence_seg.extend(self.word_seg(tmp))
            tmp.clear()
            i = j
            if i < len(word_list):
                sentence_seg.append(word_list[i])
            i += 1
        return sentence_seg

    def tokenizer(self, data_file='../../data/199801_sent.txt', target_file='../../data/seg_HMM.txt'):
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
                segList = self.line_seg(list(line))
                print(segList)
                # print(f_words)
                write_file(segList, tf)
            f.close()
            tf.close()


if __name__ == "__main__":
    hmm = HMM('../../data/h.pkl')
    hmm.tokenizer()
    # print(hmm.line_seg(['19980101-01-003-004', '（', '新华社', '记者', '樊', '如钧', '摄', '）', '\n' ]))
