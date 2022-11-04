# -*- coding: gbk -*-
from math import log

import tqdm

from lab1.tokenizers.oov.utils import IdDate
from lab1.scores import get_score
from lab1.tokenizers.fmm_bmm.MM import write_file


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


if __name__ == '__main__':
    d1 = Unigram('../../data/dict.txt')
    d1.tokenize('../../data/199801_sent.txt', '../../data/seg_Unigram.txt')
    print(get_score('../../data/199801_seg&pos.txt', '../../data/seg_Unigram.txt'))
    print(get_score('../../data/199801_seg&pos.txt', '../../data/seg_Bigram.txt'))
