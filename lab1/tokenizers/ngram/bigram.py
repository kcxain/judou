# -*- coding: gbk -*-
from math import log

import tqdm

from lab1.tokenizers.oov.utils import IdDate_all
from lab1.tokenizers.oov.utils import decode
from lab1.tokenizers.oov.utils import good_tuning_smoothing
from lab1.scores import get_score
from lab1.tokenizers.fmm_bmm.MM import write_file
from unigram import Unigram
from lab1.tokenizers.hmm.HMM import HMM


def bi_calc(words, pre_dict, next_dict, route):
    for word in words:
        if word == '<BOS>':
            route[word] = (0.0, '<BOS>')
        else:
            if word in next_dict:
                nodes = next_dict[word]
            else:
                route[word] = (-100000, '<BOS>')
                continue
            route[word] = max((pre_dict[node][word] + route[node][0], node) for node in nodes)


class Bigram(Unigram):
    def __init__(self, uni_dict, bi_dict):
        # 一元前缀词典：lfreq, 词数：ltoal
        super().__init__(uni_dict)
        self.filename = bi_dict
        # 保存二元前缀词典
        self.bi_lfreq = {}
        self.bi_total = 0
        # 生成二元词典
        self.gen_bi_pfdict()
        # Good-Tuning+对数插值平滑
        # self.N = good_tuning_smoothing(self.lfreq, self.bi_lfreq)
        # 加入HMM字成词
        self.hmm = HMM()


    def gen_bi_pfdict(self):
        """
        构建前缀词典
        :param filename: 词典
        :return: 词频，词数
        """
        with open(self.filename, encoding='gbk') as fp:
            line = fp.readline()
            while len(line) > 0:
                word1, word2, freq = line.strip().split()[0:3]
                freq = int(freq)
                if word2 not in self.bi_lfreq:
                    self.bi_lfreq[word2] = {word1: freq}
                    self.bi_total += freq
                else:
                    self.bi_lfreq[word2][word1] = freq
                    self.bi_total += freq
                line = fp.readline()

    def log_p(self, words):
        """
        计算 log(w_1 | w_2)
        :param words: 二元元组，两个单词
        :return: 返回 log(w_1 | w_2)
        """
        assert len(words) == 2
        (w1, w2) = words

        p_w1 = 0.0 if w1 not in self.lfreq else self.lfreq[w1]
        p_w12 = 0.0 if w2 not in self.bi_lfreq or w1 not in self.bi_lfreq[w2] else self.bi_lfreq[w2][w1]
        p_w1 += 0.03 * len(self.lfreq.keys())
        p_w12 += 0.01
        return log(p_w12) - log(p_w1)

        # (uni_n, bi_n) = self.N
        # r_w1 = 0 if w1 not in self.lfreq else self.lfreq[w1]
        # r_w12 = 0 if w2 not in self.bi_lfreq or w1 not in self.bi_lfreq[w2] else self.bi_lfreq[w2][w1]

        # r_w1 = (r_w1 + 1) * (float(uni_n[r_w1 + 1]) / float(uni_n[r_w1])) if r_w1 != 0 else float(uni_n[1])
        # r_w12 = (r_w12 + 1) * (float(bi_n[r_w12 + 1]) / float(bi_n[r_w12])) if r_w12 != 0 else float(bi_n[1])

        # p_w1 = float(r_w1) / float(self.ltotal)
        # p_w12 = float(r_w12) / float(self.bi_total)
        # return log(p_w12) - log(p_w1)

    def search(self, sentence, hmm_oov=False):
        """
        分词
        :param sentence:
        :return: 路径
        """
        # 未登录词：日期数字串
        # 四个等价类, 替换
        sentence, pad_dict = IdDate_all(sentence)

        # 加入开头，结尾
        sentence = '<BOS>' + sentence + '<EOS>'
        # 建立DAG图，与 Unigram 的相同
        # print(sentence)
        DAG = self._get_DAG(sentence)
        # print(DAG)
        pre_dict = {'<BOS>': {}}
        BOS = len('<BOS>')
        # 去掉<BOS>的第一个词
        for x in DAG[BOS]:
            pre_dict['<BOS>'][(BOS, x + 1)] = self.log_p(("<BOS>", sentence[BOS:x + 1]))
        # print(pre_dict['<BOS>'])
        # 对每一个字可能的分词方式生成下一个词的词典
        n = len('<BOS>')
        while n < (len(sentence) - len('<EOS>')):
            i = DAG[n]
            for x in i:
                pre = sentence[n:x + 1]
                current = x + 1
                current_idx = DAG[x + 1]
                temp = {}
                for char_i in current_idx:
                    word = sentence[current:char_i + 1]
                    # <EOS> 特殊处理
                    if word == "<":
                        temp['<EOS>'] = self.log_p((pre, '<EOS>'))
                    else:
                        temp[(current, char_i + 1)] = self.log_p((pre, word))
                pre_dict[(n, x + 1)] = temp
            n += 1
        next_dict = {}
        words = list(pre_dict.keys())
        for pre in words:
            for word in pre_dict[pre].keys():  # 遍历pre_word的后一个词
                next_dict[word] = next_dict.get(word, list())
                next_dict[word].append(pre)
        words.append('<EOS>')

        route = {}
        bi_calc(words, pre_dict, next_dict, route)
        sentence_words = []
        idx = "<EOS>"
        while idx != '<BOS>':
            idx = route[idx][1]
            if idx != '<BOS>':
                (i, j) = idx
                sentence_words.insert(0, sentence[i:j])
        # print(sentence_words)
        # 将pad还原
        decode(sentence_words, pad_dict)
        if hmm_oov:
            sentence_words = self.hmm.line_seg(sentence_words)
        return sentence_words

    def tokenize(self, data_file, target_file, hmm_oov=False):
        """
        最终分词程序
        :param data_file: 待分词的文本
        :param target_file: 分词结果输入目标文本
        """
        with open(data_file) as f:
            lines = f.readlines()
            tf = open(target_file, 'w')
            for line in tqdm.tqdm(lines):
                segList = self.search(line, hmm_oov)
                # print(segList)
                write_file(segList, tf)
            f.close()
            tf.close()


if __name__ == '__main__':
    # bi = Bigram('../../data/dict.txt', '../../data/bi_dict.txt')
    # bi.search("19980101-01-001-004１２月３１日，中共中央总书记、国家主席发表１９９８年新年讲话《迈向充满希望的新世纪》。（新华社记者红光摄）")
    # bi.tokenize('../../data/199801_sent.txt', '../../data/seg_Bigram.txt')
    # bi.tokenize('../../data/199801_sent.txt', '../../data/seg_Bigram_hmm.txt', hmm_oov=True)
    # bi.tokenize('../../data/test_in.txt', '../../data/seg_test.txt')
    print(('unigram:', get_score('../../data/199801_seg&pos.txt', '../../data/seg_Unigram.txt')))
    print(('bigram:', get_score('../../data/199801_seg&pos.txt', '../../data/seg_Bigram.txt')))
    print(('bigram_hmm:', get_score('../../data/199801_seg&pos.txt', '../../data/seg_Bigram_hmm.txt')))
