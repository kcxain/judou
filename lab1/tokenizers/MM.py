# -*- coding: gbk -*-
from abc import abstractmethod

from lab1.vocab.Vocab import Vocab
from lab1.vocab.VocabData import init_vocab


def write_file(line, tf):
    """
    把分词列表写入文件
    :param line: 分词列表
    :param tf: 文件
    :return:
    """
    for l in line:
        if l == '\n':
            tf.write('\n')
            break
        tf.write(l)
        tf.write('/ ')


class MM:
    """
    最大匹配抽象类，作为FMM和BMM的父类
    """

    def __init__(self, datatype='list'):
        vocab = Vocab()
        self.vocabData = init_vocab(datatype=datatype)
        self.pattern = vocab.get_pattern()

    @abstractmethod
    def tokenize(self):
        pass
