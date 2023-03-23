# -*- coding: gbk -*-
import re

import tqdm


class Vocab:
    def __init__(self, data_file, target_file):
        self.data_file = data_file
        self.target_file = target_file
        # ���ִ�ͳһΪ #
        self.pad = '#'
        # ����ʵ�
        self.d = dict()
        # ����������ʽƥ�����ֺ�������е��ַ�
        self.s = set()
        self.patterns = [
            # �꣬�£��գ�ʱ���֣��ٷִ�����Щ�Ƿֿ��ģ����Բ��ܺ�����ϲ�
            re.compile(r'((([��-��]|[.������ã�]|[����һ�����������߰˾�ʮ])+)[�����շ�ʱ])'),
            # ��������ĸ��
            re.compile(r'(([��-��]|[0-9]|[��-��]|[��-��]|-|��|��|��|��|��|��)+)'),
            # �ٷ���
            re.compile(
                r'(��?(�ٷ�֮|��)?[����һ�����������߰˾�ʮ��ǧ��]+[.������ã�]?([����һ�����������߰˾�ʮ])*)'),
            # ����λ������
            re.compile(r'((([��-��]|[0-9]|[.������ã�]|[����һ�����������߰˾�ʮ])+[������ǧ��]+)+)'),
        ]
        # ��������ƥ�����

    def padding_words(self, word):
        """
        :param word: ����ĵ���
        :return: ���ݵ���ƥ��������ʽ�����ƥ��ɹ������滻Ϊpad
        """
        # 19980112-09-001-001
        # ��ĸ��
        # 51073
        # pattern_index = re.compile(r'((\d|-|��|��|��|[��-��]|��|[��-��]|[��-��]|��)+)')
        # ����
        # pattern_numrate = re.compile(r'((��?(�ٷ�֮|��)?([��-��]+|[0-9]+|[����һ�����������߰˾�ʮ��]+)([��ǧ����]?)[.������]?([��-��]+|[0-9]+|['
        #                             r'����һ�����������߰˾�ʮ]+)([��ǧ����]?)([����ǧ�ڸ�����])*)+)|((\d|-|��|��|��|[��-��]|��|[��-��]|[��-��]|��)+)')
        # pattern_sentence = re.compile(r'')

        for pattern in self.patterns:
            m = pattern.match(word)
            if m is not None:
                # print(m.group(0))
                # print(m.span(0))
                index = m.span()
                # print(index)
                # ��ȫƥ��
                if index[1] == len(word):
                    # print(word)
                    # ��word�滻Ϊpad
                    word = self.pad
        return word

    def add_name(self):
        """
        �ֵ��м���������Դ
        :return:
        """
        with open('../../dict/origin_data_set/name.txt', encoding='gbk', errors='ignore') as f:
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
        :return: ����dict.txt
        """
        for file in tqdm.tqdm(self.data_file):
            with open(file, encoding='gbk') as f:
                lines = f.readlines()
                # ���ո�ָ�
                for line in lines:
                    if line is None:
                        continue
                    word_list = line.split()
                    for word in word_list:
                        # word.replace('[', '') �޷������滻
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
        ��Ԫ�ķ��ʵ�
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
            assert (len(words[0]) == 2)
            for word in words:
                f.write(word[0][0])
                f.write('\t')
                f.write(word[0][1])
                f.write('\t')
                f.write(str(word[1]))
                if word is not words[-1]:
                    f.write('\n')
            f.close()

    def get_padded_words(self):
        """
        :return: ���ر�padding���Ŀ��ܵ��ַ�
        """
        return self.s.copy()

    def get_pattern(self):
        """
        :return: ������ĸ�����õ��������
        """
        return self.patterns


def get_sorted_list(dict_in, reverse=False):
    """
    ���ʵĴ�С����
    :param dict_in: �ʵ�
    :param reverse: False Ϊ����TrueΪ����
    :return: ����õ��б�
    """
    return sorted(dict_in.items(), key=lambda x: x[1], reverse=reverse)
