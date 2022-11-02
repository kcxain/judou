# -*- coding: gbk -*-
from math import log


class DynamicSearch:
    def __init__(self, dict):
        self.filename = dict
        self.lfreq = {}  # 保存前缀词典
        self.ltotal = 0  # 保存总的词数

    def search(self, sentence):
        """
        分词
        :param sentence:
        :return: 路径
        """
        # 构建前缀词典
        self.gen_pfdict()
        DAG = self._get_DAG(sentence)
        route = {}
        self._clac(sentence, DAG, route)
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

    def _clac(self, sentence, DAG, route):
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
                (log(self.lfreq[sentence[idx:x + 1]] or 1) - logtotal + route[x + 1][0], x) for x in DAG[idx])


if __name__ == '__main__':
    d1 = DynamicSearch('../data/dict.txt')
    print(d1.search("今0 天1 真2 是3 个4 好5 日6 子7 ，8 我9 要10 去11 北12 京13 人14 民15 大16 会17 堂18 玩19 ！20"))

