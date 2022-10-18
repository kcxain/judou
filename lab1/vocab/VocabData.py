# -*- coding: gbk -*-
from abc import abstractmethod

from lab1.vocab.Vocab import Vocab


def init_vocab(datafile='../data/dict.txt', datatype=list):
    """
    静态工厂方法，指定某种数据结构，并初始化词典
    :param datafile: 词典存放的本地文件
    :param datatype: 指定数据结构
    :return: 根据指定数据结构生成的词典
    """
    vocab_data = VocabData()
    if datatype == "list":
        vocab_data = VocabList()
    f = open(datafile, encoding='gbk')
    lines = f.readlines()
    for line in lines:
        if line is None:
            continue
        word = line.split('\t')[0]
        vocab_data.add(word)
    return vocab_data


class VocabData:
    """
    抽象类定义字典存储的数据结构
    """

    def __init__(self):
        self.vocab = Vocab()
        self.maxlen = 0

    def maxLen(self):
        """
        :return:词典中最大词的长度
        """
        return self.maxlen

    @abstractmethod
    def __contains__(self, item):
        """
        重写__contains__方法，用于查找词典
        :param item: 要查找的字符串
        :return: BOOL，是否存在
        """
        pass

    @abstractmethod
    def add(self, item):
        """
        向词典添加元素
        :param item: 元素
        :return: None
        """
        pass


class VocabList(VocabData):
    """
    使用Python的list存储词典，对应于3.2
    """

    def __init__(self):
        super(VocabList, self).__init__()
        self.dict = list()

    def __contains__(self, item):
        return self.dict.__contains__(item)

    def add(self, item):
        self.dict.append(item)
        # 维护最大分词长度
        self.maxlen = max(self.maxlen, len(item))

    def __repr__(self):
        return self.dict.__repr__()

    def __len__(self):
        return len(self.dict)
