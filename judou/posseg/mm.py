# -*- coding: gbk -*-
from abc import abstractmethod

from ..dict_reader.Vocab import Vocab
from ..dict_reader.VocabData import init_vocab
import re
import tqdm

pattern_numrate = re.compile(r'((��*(�ٷ�֮|��)?([��-��]+|[0-9]+|[����һ�����������߰˾�ʮ��]+|[��-��]+|[��-��]+|-)+([��ǧ����]?)['
                             r'.������ã�]*([��-��]*|[0-9]*|[ '
                             r'����һ�����������߰˾�ʮ]*)([��ǧ����]?)([����ǧ�ڸ�����])*)+)')


def write_file(line, tf):
    """
    �ѷִ��б�д���ļ�
    :param line: �ִ��б�
    :param tf: �ļ�
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
    ���ƥ������࣬��ΪFMM��BMM�ĸ���
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
        # ��������ƥ��ֳ�������ĸ��
        l = self.pattern.finditer(line)
        # ����������Ӵʵ���
        for w in l:
            # ����ƥ�䵽���±�
            (i, j) = w.span()
            # ��ֹ����ƥ����ȷ���
            if i == 0 and j > 19:
                j = 19
            self.vocabData.add(line[i:j])
        # print(self.vocabData)
        # �������ƥ���㷨
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
        # ��������ƥ��ֳ�������ĸ��
        l = self.pattern.finditer(line)
        # ����������Ӵʵ���
        for w in l:
            # ����ƥ�䵽���±�
            (i, j) = w.span()
            # ��ֹ������ȷ���
            if i == 0 and j > 19:
                j = 19
            self.vocabData.add(line[i:j])
        # print(self.vocabData)
        # �������ƥ���㷨
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
