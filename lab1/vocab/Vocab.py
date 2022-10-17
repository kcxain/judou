# -*- coding: gbk -*-
import re


class Vocab:
    def __init__(self, data_file='../data/199801_seg&pos.txt', target_file='../data/dict.txt'):
        self.data_file = data_file
        self.target_file = target_file
        # 数字串统一为<n>
        self.pad = '<n>'
        # 保存词典
        self.d = dict()
        # 保存正则表达式匹配数字后面可能有的字符
        self.s = set()
        # 保存全部正则匹配规则
        # self.patterns = list()

    def padding_words(self, word):
        """
        :param word: 读入的单词
        :return: 根据单词匹配正则表达式，如果匹配成功则将其替换为pad
        """
        # 19980112-09-001-001
        # 字母串
        # 51073
        pattern_index = re.compile(r'((\d|-|∶|．|／|[０-９]|·|[ａ-ｚ]|[Ａ-Ｚ]|—)+)')
        # 数字
        pattern_numrate = re.compile(r'(—?(百分之|第)?([０-９]+|[0-9]+|[○零一二三四五六七八九十百]+)([百千万亿]?)[.．·点]?([０-９]+|[0-9]+|['
                                     r'○零一二三四五六七八九十]+)([百千万亿]?)([年万千亿个％‰])*)*')
        # pattern_sentence = re.compile(r'')

        # 如果加入数组中遍历太慢了，只能这样
        m1 = pattern_index.match(word)
        m2 = pattern_numrate.match(word)
        if m1 is not None:
            # print(m.group(0))
            # print(m.span(0))
            index1 = m1.span()
            # print(index)
            # 完全匹配
            if index1[1] == len(word):
                # print(word)
                # 将word替换为pad
                word = self.pad
        if word is self.pad:
            return word
        if m2 is not None:
            # print(m.group(0))
            # print(m.span(0))
            index2 = m2.span()
            # print(index)
            # 完全匹配
            if index2[1] == len(word):
                # print(word)
                # 将word替换为pad
                word = self.pad
        return word

    def make_vocab(self):
        """
        :return: 生成dict.txt
        """
        with open(self.data_file, encoding='gbk') as f:
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

                    if single_word not in self.d:
                        self.d[single_word] = 1
                    else:
                        self.d[single_word] += 1
            f.close()

        with open(self.target_file, 'w', encoding='gbk') as f:
            words = get_sorted_list(self.d)
            for word in words:
                f.write(word[0])
                f.write('\t')
                f.write(str(word[1]))
                if word is not words[-1]:
                    f.write('\n')
            f.close()

    def get_vocab_list(self):
        """
        将词典存储到list中
        :return: list,词典
        """
        vocab = list()
        try:
            f = open(self.target_file)
            f.close()
        except FileNotFoundError:
            self.make_vocab()
        with open(self.target_file, encoding='gbk') as f:
            lines = f.readlines()
            for line in lines:
                if line is None:
                    continue
                word = line.split('\t')[0]
                vocab.append(word)
        return vocab

    def get_paddedwords(self):
        """
        :return: 返回被padding过的可能的字符
        """
        return self.s.copy()


def get_sorted_list(dict_in, reverse=False):
    """
    按词的大小排序
    :param dict_in: 词典
    :param reverse: False 为升序，True为降序
    :return: 排序好的列表
    """
    return sorted(dict_in.items(), key=lambda x: len(x[0]), reverse=reverse)


if __name__ == '__main__':
    vocab = Vocab()
    vocab.make_vocab()
