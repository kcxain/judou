# -*- coding: gbk -*-
import pickle
import re
from math import log

import tqdm

# ��Сֵ
MIN_FLOAT = -3.14e100
pre = {'B': 'ES', 'M': 'MB', 'S': 'SE', 'E': 'BM'} # ��״̬֮ǰ���Գ��ֵ�״̬
states = ['B', 'M', 'E', 'S']  # ״̬��
date_pattern = '[0-9]*[-][0-9]*[-][0-9]{3}[-][0-9]{3}'


class train():
    """
    ѵ��HMM����
    """

    def __init__(self, model_path):
        # ��ʼ״̬�ֲ�
        self.pi = {}
        # ״̬ת�ƾ���
        self.A = {}
        # �������
        self.B = {}
        self.num = 0
        self.words = set()
        # ÿ��״̬����Ŀ
        self.state_num = {}
        # ģ�ͱ����ַ
        self.model_path = model_path
        # ȫ����ʼ��Ϊ0
        for state in states:
            self.state_num[state] = 0.0
            self.pi[state] = 0.0
            self.A[state] = {}
            self.B[state] = {}
            for temp_state in states:
                self.A[state][temp_state] = 0.0

    def tag(self, line):
        """
        ��ע�ı������ֹ���
        :param line: ������ı�
        :return: tag
        """
        line_word = []
        line_tag = []
        for word in line.split():
            word = word[1 if word[0] == '[' else 0:word.index('/')]
            self.num += 1
            if len(word) == 0:
                continue
            if word[-1] == ']':
                word = word[0:-1]

            line_word.extend(list(word))
            self.words.add(word)
            # ����
            if len(word) == 1:
                self.pi['S'] += 1
                line_tag.append('S')
            else:
                self.pi['B'] += 1
                # ��ʼ״ֻ̬����B��S
                # self.pi['E'] += 1
                # self.pi['M'] += len(word) - 2
                line_tag.append('B')
                line_tag.extend(['M'] * (len(word) - 2))
                line_tag.append('E')
        assert len(line_tag) == len(line_word)
        return line_word, line_tag

    def train_text(self, train_file=None):

        if train_file is None:
            train_file = ['../../data/origin_data_set/199801_seg&pos.txt', '../../data/origin_data_set/199802.txt', '../../data/origin_data_set/199803.txt',
                          '../../data/origin_data_set/name_pre.txt']

        assert train_file is not None

        for file in train_file:
            with open(file, encoding='gbk', errors='ignore') as f:
                lines = f.readlines()
                for line in tqdm.tqdm(lines):
                    if line is None or line == '\n':
                        continue
                    line = re.sub(date_pattern, '', line)
                    word, tag = self.tag(line)
                    # print(word)
                    # print(tag)
                    for i in range(len(tag)):
                        self.state_num[tag[i]] += 1
                        self.B[tag[i]][word[i]] = self.B[tag[i]].get(word[i], 0) + 1
                        if i > 0:
                            self.A[tag[i - 1]][tag[i]] += 1
                f.close()
        self.update_model()

    def save_model(self):
        """
        ����HMMѵ������
        :return:
        """
        with open(self.model_path, "wb") as f:
            pickle.dump(self.pi, f)
            pickle.dump(self.A, f)
            pickle.dump(self.B, f)
        f.close()

    def update_model(self):
        """
        ���¼�����ʾ���
        :return:
        """
        for state in states:
            a = 0.00001
            # ����״̬
            self.pi[state] = MIN_FLOAT if self.pi[state] == 0 else log((self.pi[state]) / self.num)
            for temp_state in states:
                self.A[state][temp_state] = MIN_FLOAT if self.A[state][temp_state] == 0 else log((self.A[state][temp_state]) / (self.state_num[state]))
            for word in self.B[state].keys():
                self.B[state][word] = MIN_FLOAT if self.B[state][word] == 0 else log((self.B[state][word]) / (self.state_num[state]))
