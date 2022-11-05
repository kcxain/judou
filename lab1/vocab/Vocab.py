# -*- coding: gbk -*-
import re

import tqdm


class Vocab:
    def __init__(self, data_file=None,
                 target_file='../data/dict.txt'):
        if data_file is None:
            data_file = ['../data/199801_seg&pos.txt', '../data/199802.txt', '../data/199803.txt']
            data_file = ['../data/199802.txt', '../data/199803.txt']
        self.data_file = data_file
        self.target_file = target_file
        # 数字串统一为 #
        self.pad = '#'
        # 保存词典
        self.d = dict()
        # 保存正则表达式匹配数字后面可能有的字符
        self.s = set()
        self.patterns = [
            # 年，月，日，时，分，再分词中这些是分开的，所以不能和上面合并
            re.compile(r'((([０-９]|[.．·点∶／]|[○零一二三四五六七八九十])+)[年月日分时])'),
            # 纯数字字母串
            re.compile(r'(([０-９]|[0-9]|[ａ-ｚ]|[Ａ-Ｚ]|-|．|∶|／|·|—|－)+)'),
            # 百分数
            re.compile(
                r'(—?(百分之|第)?[○零一二三四五六七八九十百千万]+[.．·点∶／]?([○零一二三四五六七八九十])*)'),
            # 带单位的数字
            re.compile(r'((([０-９]|[0-9]|[.．·点∶／]|[○零一二三四五六七八九十])+[百亿万千％]+)+)'),
        ]
        # 保存正则匹配规则

    def padding_words(self, word):
        """
        :param word: 读入的单词
        :return: 根据单词匹配正则表达式，如果匹配成功则将其替换为pad
        """
        # 19980112-09-001-001
        # 字母串
        # 51073
        # pattern_index = re.compile(r'((\d|-|∶|．|／|[０-９]|·|[ａ-ｚ]|[Ａ-Ｚ]|—)+)')
        # 数字
        # pattern_numrate = re.compile(r'((—?(百分之|第)?([０-９]+|[0-9]+|[○零一二三四五六七八九十百]+)([百千万亿]?)[.．·点]?([０-９]+|[0-9]+|['
        #                             r'○零一二三四五六七八九十]+)([百千万亿]?)([年万千亿个％‰])*)+)|((\d|-|∶|．|／|[０-９]|·|[ａ-ｚ]|[Ａ-Ｚ]|—)+)')
        # pattern_sentence = re.compile(r'')

        # 因为Python遍历数组太慢了，只能这样
        for pattern in self.patterns:
            m = pattern.match(word)
            if m is not None:
                # print(m.group(0))
                # print(m.span(0))
                index = m.span()
                # print(index)
                # 完全匹配
                if index[1] == len(word):
                    # print(word)
                    # 将word替换为pad
                    word = self.pad
        return word

    def add_name(self):
        """
        字典中加入人名资源
        :return:
        """
        with open('../data/name.txt', encoding='gbk', errors='ignore') as f:
            lines = f.readlines()
            for line in lines:
                word = line.strip()
                if word is None:
                    continue
                if word not in self.d:
                    self.d[word] = 1
                else:
                    self.d[word] += 1

    def make_vocab(self):
        """
        :return: 生成dict.txt
        """
        for file in tqdm.tqdm(self.data_file):
            with open(file, encoding='gbk') as f:
                lines = f.readlines()
                # 按空格分割
                for line in lines:
                    if line is None:
                        continue
                    word_list = line.split()
                    for word in word_list:
                        # word.replace('[', '') 无法正常替换
                        if word[0] == '[':
                            new_word = word[1:]
                            word = new_word
                        word.replace(']', '')
                        # print(word)
                        w = word.split('/')
                        single_word = w[0]
                        single_word = self.padding_words(single_word)
                        if single_word == '#':
                            continue
                        if single_word not in self.d:
                            self.d[single_word] = 1
                        else:
                            self.d[single_word] += 1
                f.close()

        # self.add_name()

        with open(self.target_file, 'w', encoding='gbk') as f:
            words = get_sorted_list(self.d)
            for word in words:
                f.write(word[0])
                f.write('\t')
                f.write(str(word[1]))
                if word is not words[-1]:
                    f.write('\n')
            f.close()

    def make_biVocab(self, bi_dict):
        """
        二元文法词典
        :return:
        """
        d = {}
        for file in tqdm.tqdm(self.data_file):
            with open(file, 'r') as f:
                lines = f.readlines()
            for line in lines:
                if line is None:
                    continue
                word_list = ['<BOS>']
                origin_list = line.split()

                for word in origin_list:
                    if word[0] == '[':
                        new_word = word[1:]
                        word = new_word
                    word.replace(']', '')
                    w = word.split('/')
                    single_word = w[0]
                    single_word = self.padding_words(single_word)
                    if single_word == '#':
                        continue
                    word_list.append(single_word)
                word_list.append('<EOS>')
                for i in range(len(word_list) - 1):
                    word_pair = (word_list[i], word_list[i + 1])
                    if word_pair not in d:
                        d[word_pair] = 1
                    else:
                        d[word_pair] += 1
            f.close()

        with open(bi_dict, 'w', encoding='gbk') as f:
            words = get_sorted_list(d)
            assert(len(words[0]) == 2)
            for word in words:
                f.write(word[0][0])
                f.write('\t')
                f.write(word[0][1])
                f.write('\t')
                f.write(str(word[1]))
                if word is not words[-1]:
                    f.write('\n')
            f.close()

    def get_paddedwords(self):
        """
        :return: 返回被padding过的可能的字符
        """
        return self.s.copy()

    def get_pattern(self):
        """
        :return: 数字字母串所用的正则规则
        """
        return self.patterns


def get_sorted_list(dict_in, reverse=False):
    """
    按词的大小排序
    :param dict_in: 词典
    :param reverse: False 为升序，True为降序
    :return: 排序好的列表
    """
    return sorted(dict_in.items(), key=lambda x: x[1], reverse=reverse)


if __name__ == '__main__':
    vocab = Vocab()
    vocab.make_vocab()
    vocab.make_biVocab('../data/bi_dict.txt')
