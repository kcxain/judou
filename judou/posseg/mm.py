# -*- coding: gbk -*-
from abc import abstractmethod

from ..dict_reader.Vocab import Vocab
from ..dict_reader.VocabData import init_vocab
import re
import tqdm

pattern_numrate = re.compile(r'((—*(百分之|第)?([０-９]+|[0-9]+|[○零一二三四五六七八九十百]+|[ａ-ｚ]+|[Ａ-Ｚ]+|-)+([百千万亿]?)['
                             r'.．·点∶／]*([０-９]*|[0-9]*|[ '
                             r'○零一二三四五六七八九十]*)([百千万亿]?)([年万千亿个％‰])*)+)')


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
        self.pattern = pattern_numrate

    @abstractmethod
    def tokenize(self):
        pass


class FMM(MM):
    def __init__(self, data_file, target_file, datatype='list'):
        super().__init__(datatype=datatype)
        self.data_file = data_file
        self.target_file = target_file

    def tokenize(self):
        with open(self.data_file) as f:
            lines = f.readlines()
            tf = open(self.target_file, 'w')
            for line in tqdm.tqdm(lines):
                self.tokenize_line(line, tf)
            f.close()
            tf.close()

    def tokenize_line(self, line, tf):
        # 先用正则匹配分出数字字母串
        l = self.pattern.finditer(line)
        # 先用正则添加词典中
        for w in l:
            # 正则匹配到的下标
            (i, j) = w.span()
            # 防止正则匹配过度泛化
            if i == 0 and j > 19:
                j = 19
            self.vocabData.add(line[i:j])
        # print(self.vocabData)
        # 正向最大匹配算法
        segList = []
        maxlen = self.vocabData.maxlen
        while len(line) > 0:
            length = self.vocabData.maxlen
            if len(line) < maxlen:
                length = len(line)
            tryWord = line[0:length]
            while tryWord not in self.vocabData:
                if len(tryWord) == 1:
                    break
                tryWord = tryWord[0:len(tryWord) - 1]
            segList.append(tryWord)
            line = line[len(tryWord):]
        print(segList)
        write_file(segList, tf)


class BMM(MM):
    def __init__(self, data_file, target_file, datatype='list'):
        super().__init__(datatype=datatype)
        self.data_file = data_file
        self.target_file = target_file

    def tokenize(self):
        with open(self.data_file) as f:
            lines = f.readlines()
            tf = open(self.target_file, 'w')
            for line in tqdm.tqdm(lines):
                self.tokenize_line(line, tf)
            f.close()
            tf.close()

    def tokenize_line(self, line, tf):
        # 先用正则匹配分出数字字母串
        l = self.pattern.finditer(line)
        # 先用正则添加词典中
        for w in l:
            # 正则匹配到的下标
            (i, j) = w.span()
            # 防止正则过度泛化
            if i == 0 and j > 19:
                j = 19
            self.vocabData.add(line[i:j])
        # print(self.vocabData)
        # 正向最大匹配算法
        segList = []
        maxlen = self.vocabData.maxlen
        while len(line) > 0:
            length = self.vocabData.maxlen
            if len(line) < maxlen:
                length = len(line)
            tryWord = line[len(line) - length:]
            while tryWord not in self.vocabData:
                if len(tryWord) == 1:
                    break
                tryWord = tryWord[1:]
            segList.insert(0, tryWord)
            line = line[:len(line) - len(tryWord)]
        print(segList)
        write_file(segList, tf)
