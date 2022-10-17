# -*- coding: gbk -*-
from lab1.vocab.Vocab import Vocab

class MM:
    """
    最大匹配抽象类，作为FMM和BMM的父类
    """

    def __init__(self):
        vocab = Vocab()
        self.vocab_list = vocab.get_vocab_list()
        self.maxLen = self.getmaxlen()

    def getmaxlen(self):
        """
        计算词典中最长词的长度
        :return: 返回最长词长度
        """
        maxLen = 0
        for word in self.vocab_list:
            if len(word) > maxLen:
                maxLen = len(word)
        return maxLen

    def tokenize(self):
        raise NotImplemented
