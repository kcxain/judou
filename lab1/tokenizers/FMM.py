# -*- coding: gbk -*-
from lab1.tokenizers.MM import MM
import re


class FMM(MM):
    def __init__(self, data_file='../data/199801_sent.txt', target_file='../data/seg_FMM.txt'):
        super().__init__()
        self.data_file = data_file
        self.target_file = target_file

    def tokenize(self):
        with open(self.data_file) as f:
            lines = f.readlines()
            for line in lines:
                self.tokenize_line(line)
            f.close()

    def tokenize_line(self, line):
        pattern_index = re.compile(r'((\d|-|∶|．|／|[０-９]|·|[ａ-ｚ]|[Ａ-Ｚ]|—)+)')
        # 数字
        pattern_numrate = re.compile(r'(—?(百分之|第)?([０-９]+|[0-9]+|[○零一二三四五六七八九十百]+)([百千万亿]?)[.．·点]?([０-９]+|[0-9]+|['
                                     r'○零一二三四五六七八九十]+)([百千万亿]?)([年万千亿个％‰])*)+')
        # 先用正则匹配分出数字字母串
        l1 = pattern_index.finditer(line)
        l2 = pattern_numrate.finditer(line)
        f = open(self.target_file)
        for i in l1:
            print(i.span())



if __name__ == '__main__':
    fmm = FMM()
    fmm.tokenize()


