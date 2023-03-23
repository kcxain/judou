# -*- coding: gbk -*-
from abc import abstractmethod

from .Vocab import Vocab


def init_vocab(datafile='../../data/dict/uni_dict.txt', datatype=list):
    """
    静态工厂方法，指定某种数据结构，并初始化词典
    :param datafile: 词典存放的本地文件
    :param datatype: 指定数据结构
    :return: 根据指定数据结构生成的词典
    """
    vocab_data = VocabData()
    if datatype == "list":
        vocab_data = VocabList()
    if datatype == "set":
        vocab_data = VocabSet()
    f = open(datafile, encoding='gbk')
    lines = f.readlines()
    for line in lines:
        if line is None:
            continue
        word = line.split('\t')[0]
        # 调用对应数据结构的add方法
        vocab_data.add(word)
    f.close()
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
        # print(item)
        self.dict.append(item)
        # 维护最大分词长度
        self.maxlen = max(self.maxlen, len(item))

    def __repr__(self):
        return self.dict.__repr__()

    def __len__(self):
        return len(self.dict)


class VocabSet(VocabData):
    """
    哈希表存储词典，拉链法
    """

    def __init__(self, size=30000):
        super(VocabSet, self).__init__()
        self._size = size
        # 元素个数
        self._filled = 0
        # 线性表首地址
        self._element = [[] for _ in range(size)]

    def _hash_function(self, value):
        """
        哈希函数
        :param value:
        :return: hash(value)
        """
        return hash(value) % self._size

    def _contains(self, value):
        """
        :return: 返回对应线性表中元素个数，如果不存在则返回-1
        """
        for i, e in enumerate(self._element[self._hash_function(value)]):
            if value == e:
                return i
        return -1

    def contains(self, value):
        """
        :return: 元素存在则返回True,否则返回False
        """
        return self._contains(value) >= 0

    def add(self, value):
        """
        添加元素
        """
        self._filled += 1
        self.maxlen = max(self.maxlen, len(value))
        # print(value)
        self._element[self._hash_function(value)].append(value)
        # self._resize()

    def delete(self, value):
        """
        删除元素
        """
        index = self._contains(value)
        if index >= 0:
            self._filled -= 1
            self._element[self._hash_function(value)].pop(index)
            self._resize()

    def _resize(self):
        """
        重新整理散列表
        """
        # 最高装填因子
        RESIZE_FACTOR_UP = 1 / 2
        # 最低装填因子
        RESIZE_FACTOR_DOWN = 1 / 3
        # 最小大小
        MIN_SIZE = 1000
        # 装填因子
        capacity_ratio = float(self._filled) / self._size
        # 装填因子太低，并且
        if capacity_ratio < RESIZE_FACTOR_DOWN and self._size / 2 >= MIN_SIZE:
            self._create_resized_array(self._size / 2)
        # 装填因子过高，则增大size，降低冲突概率
        if capacity_ratio > RESIZE_FACTOR_UP:
            self._create_resized_array(self._size * 2)

    def _create_resized_array(self, new_size):
        """
        根据size,重新建立散列表
        """
        new_element_array = [[] for _ in range(int(new_size))]
        self._size = len(new_element_array)
        for l in self._element:
            for e in l:
                new_element_array[self._hash_function(e)].append(e)
        self._element = new_element_array

    def __iter__(self):
        for l in self._element:
            if l:
                for e in l:
                    yield e
        raise StopIteration()

    def __repr__(self):
        res = list()
        for l in self._element:
            if l:
                for e in l:
                    res += e
        return res

    def __contains__(self, item):
        return self.contains(item)
