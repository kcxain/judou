# -*- coding: gbk -*-
from math import log

import tqdm

from .mm import write_file
from .hmm import HMM
from .utils import IdDate_all, decode, IdDate


def IdDate_route(line, route):
    """
    替换route
    :param line:
    :param route:
    :return:
    """
    data_idx = IdDate(line)
    # 根据未登录词表修改路径
    # 这里的算法可能不太好，或许需要改进 TODO
    for (i, j) in data_idx:
        # print((i, j))
        for ii in range(i, j - 1):
            # 把最大概率的终点都改成j
            # tuple只可读不可写
            route[ii] = (route[ii][0], j - 1)
    return route


def bi_calc(words, pre_dict, next_dict, route):
    for word in words:
        if word == '<BOS>':
            route[word] = (0.0, '<BOS>')
        else:
            if word in next_dict:
                nodes = next_dict[word]
            else:
                route[word] = (-100000, '<BOS>')
                continue
            route[word] = max((pre_dict[node][word] + route[node][0], node) for node in nodes)


class Unigram:
    def __init__(self, dict):
        self.filename = dict
        self.lfreq = {}  # 保存前缀词典
        self.ltotal = 0  # 保存总的词数
        # 构建前缀词典
        self.gen_pfdict()

    def search(self, sentence):
        """
        分词
        :param sentence:
        :return: 路径
        """
        DAG = self._get_DAG(sentence)
        route = {}
        self._calc(sentence, DAG, route)
        return route

    def gen_pfdict(self):
        """
        构建前缀词典
        :param filename: 词典
        :return: 词频，词数
        """
        with open(self.filename, encoding='gbk') as fp:
            line = fp.readline()
            while len(line) > 0:
                word, freq = line.strip().split()[0:2]
                freq = int(freq)
                self.lfreq[word] = freq
                self.ltotal += freq
                # 对于离线词典的每个词，获取其前缀词
                for ch in range(len(word)):
                    wfrag = word[:ch + 1]
                    if wfrag not in self.lfreq:
                        self.lfreq[wfrag] = 0
                line = fp.readline()

    def _get_DAG(self, sentence):
        """
        生成DAG图
        :param sentence: 目标句子
        :param lfreq: 前缀词频
        :return: DAG图
        """
        DAG = {}
        N = len(sentence)
        for k in range(N):
            tmplist = []
            i = k
            frag = sentence[k]
            while i < N and frag in self.lfreq:
                if self.lfreq[frag] > 0:
                    tmplist.append(i)
                i += 1
                frag = sentence[k:i + 1]
            if not tmplist:
                tmplist.append(k)
            DAG[k] = tmplist
        return DAG

    def _calc(self, sentence, DAG, route):
        """
        动态规划计算
        :param sentence: 句子
        :param DAG: 生成的DAG图
        :param route: 动态规划路径
        :param lfreq: 前缀词频
        :param ltotal: 总词数
        """
        N = len(sentence)
        route[N] = (0, 0)
        logtotal = log(self.ltotal)
        for idx in range(N - 1, -1, -1):
            route[idx] = max(
                (log(1 or self.lfreq[sentence[idx:x + 1]]) - logtotal + route[x + 1][0], x) for x in DAG[idx])

    def tokenize(self, data_file, target_file):
        """
        最终分词程序
        :param data_file: 待分词的文本
        :param target_file: 分词结果输入目标文本
        """
        with open(data_file) as f:
            lines = f.readlines()
            tf = open(target_file, 'w')
            for line in tqdm.tqdm(lines):
                segList = []
                route = self.search(line)
                # 未登录词识别：日期，数字串等
                IdDate_route(line, route)
                # print(route)
                i = 0
                while i < len(line):
                    segList.append(line[i:route[i][1] + 1])
                    i = route[i][1] + 1
                write_file(segList, tf)
            f.close()
            tf.close()


class Bigram(Unigram):
    def __init__(self, uni_dict, bi_dict, hmm_model):
        # 一元前缀词典：lfreq, 词数：ltoal
        super().__init__(uni_dict)
        self.filename = bi_dict
        # 保存二元前缀词典
        self.bi_lfreq = {}
        self.bi_total = 0
        # 生成二元词典
        self.gen_bi_pfdict()
        # Good-Tuning+对数插值平滑
        # self.N = good_tuning_smoothing(self.lfreq, self.bi_lfreq)
        # 加入HMM字成词
        self.hmm = HMM(hmm_model)

    def gen_bi_pfdict(self):
        """
        构建前缀词典
        :param filename: 词典
        :return: 词频，词数
        """
        with open(self.filename, encoding='gbk') as fp:
            line = fp.readline()
            while len(line) > 0:
                word1, word2, freq = line.strip().split()[0:3]
                freq = int(freq)
                if word2 not in self.bi_lfreq:
                    self.bi_lfreq[word2] = {word1: freq}
                    self.bi_total += freq
                else:
                    self.bi_lfreq[word2][word1] = freq
                    self.bi_total += freq
                line = fp.readline()

    def log_p(self, words):
        """
        计算 log(w_1 | w_2)
        :param words: 二元元组，两个单词
        :return: 返回 log(w_1 | w_2)
        """
        assert len(words) == 2
        (w1, w2) = words

        p_w1 = 0.0 if w1 not in self.lfreq else self.lfreq[w1]
        p_w12 = 0.0 if w2 not in self.bi_lfreq or w1 not in self.bi_lfreq[w2] else self.bi_lfreq[w2][w1]
        p_w1 += 0.03 * len(self.lfreq.keys())
        p_w12 += 0.01
        return log(p_w12) - log(p_w1)

        # (uni_n, bi_n) = self.N
        # r_w1 = 0 if w1 not in self.lfreq else self.lfreq[w1]
        # r_w12 = 0 if w2 not in self.bi_lfreq or w1 not in self.bi_lfreq[w2] else self.bi_lfreq[w2][w1]

        # r_w1 = (r_w1 + 1) * (float(uni_n[r_w1 + 1]) / float(uni_n[r_w1])) if r_w1 != 0 else float(uni_n[1])
        # r_w12 = (r_w12 + 1) * (float(bi_n[r_w12 + 1]) / float(bi_n[r_w12])) if r_w12 != 0 else float(bi_n[1])

        # p_w1 = float(r_w1) / float(self.ltotal)
        # p_w12 = float(r_w12) / float(self.bi_total)
        # return log(p_w12) - log(p_w1)

    def search(self, sentence, hmm_oov=False):
        """
        分词
        :param sentence:
        :return: 路径
        """
        # 未登录词：日期数字串
        # 四个等价类, 替换
        sentence, pad_dict = IdDate_all(sentence)

        # 加入开头，结尾
        sentence = '<BOS>' + sentence + '<EOS>'
        # 建立DAG图，与 Unigram 的相同
        # print(sentence)
        DAG = self._get_DAG(sentence)
        # print(DAG)
        pre_dict = {'<BOS>': {}}
        BOS = len('<BOS>')
        # 去掉<BOS>的第一个词
        for x in DAG[BOS]:
            pre_dict['<BOS>'][(BOS, x + 1)] = self.log_p(("<BOS>", sentence[BOS:x + 1]))
        # print(pre_dict['<BOS>'])
        # 对每一个字可能的分词方式生成下一个词的词典
        n = len('<BOS>')
        while n < (len(sentence) - len('<EOS>')):
            i = DAG[n]
            for x in i:
                pre = sentence[n:x + 1]
                current = x + 1
                current_idx = DAG[x + 1]
                temp = {}
                for char_i in current_idx:
                    word = sentence[current:char_i + 1]
                    # <EOS> 特殊处理
                    if word == "<":
                        temp['<EOS>'] = self.log_p((pre, '<EOS>'))
                    else:
                        temp[(current, char_i + 1)] = self.log_p((pre, word))
                pre_dict[(n, x + 1)] = temp
            n += 1
        next_dict = {}
        words = list(pre_dict.keys())
        for pre in words:
            for word in pre_dict[pre].keys():  # 遍历pre_word的后一个词
                next_dict[word] = next_dict.get(word, list())
                next_dict[word].append(pre)
        words.append('<EOS>')

        route = {}
        bi_calc(words, pre_dict, next_dict, route)
        sentence_words = []
        idx = "<EOS>"
        while idx != '<BOS>':
            idx = route[idx][1]
            if idx != '<BOS>':
                (i, j) = idx
                sentence_words.insert(0, sentence[i:j])
        # print(sentence_words)
        # 将pad还原
        decode(sentence_words, pad_dict)
        if hmm_oov:
            sentence_words = self.hmm.line_seg(sentence_words)
        return sentence_words

    def tokenize(self, data_file, target_file, hmm_oov=False):
        """
        最终分词程序
        :param data_file: 待分词的文本
        :param target_file: 分词结果输入目标文本
        """
        with open(data_file) as f:
            lines = f.readlines()
            tf = open(target_file, 'w')
            for line in tqdm.tqdm(lines):
                segList = self.search(line, hmm_oov)
                # print(segList)
                write_file(segList, tf)
            f.close()
            tf.close()
