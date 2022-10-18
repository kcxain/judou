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
        # 保存正则匹配规则
        self.pattern_numrate = re.compile(r'((—*(百分之|第)?([０-９]+|[0-9]+|[○零一二三四五六七八九十百]+|[ａ-ｚ]+|[Ａ-Ｚ]+|-)+([百千万亿]?)['
                                          r'.．·点∶／]?([０-９]*|[0-9]*|[ '
                                          r'○零一二三四五六七八九十]*)([百千万亿]?)([年万千亿个％‰])*)+)')

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
        m = self.pattern_numrate.match(word)
        if m is not None:
            # print(m.group(0))
            # print(m.span(0))
            index = m.span()
            # print(index)
            # 完全匹配
            if index[1] == len(word):
                print(word)
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

    def get_paddedwords(self):
        """
        :return: 返回被padding过的可能的字符
        """
        return self.s.copy()

    def get_pattern(self):
        """
        :return: 数字字母串所用的正则规则
        """
        return self.pattern_numrate


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
