# -*- coding: gbk -*-
from lab1.tokenizers.MM import MM
import re


class FMM(MM):
    def __init__(self, datatype='list', data_file='../data/199801_sent.txt', target_file='../data/seg_FMM.txt'):
        super().__init__(datatype=datatype)
        self.data_file = data_file
        self.target_file = target_file

    def tokenize(self):
        with open(self.data_file) as f:
            lines = f.readlines()
            for line in lines:
                self.tokenize_line(line)
            f.close()

    def tokenize_line(self, line):
        # 先用正则匹配分出数字字母串
        l = self.pattern.finditer(line)
        f = open(self.target_file)
        for s in l:
            (i, j) = s.span()
            print(s)


if __name__ == '__main__':
    fmm = FMM()
    print(fmm.vocabData.maxlen)
