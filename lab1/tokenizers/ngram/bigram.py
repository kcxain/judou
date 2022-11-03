# -*- coding: gbk -*-
from lab1.tokenizers.oov.utils import IdDate_all
from lab1.tokenizers.fmm_bmm.MM import write_file
from lab1.tokenizers.oov.utils import decode
from lab1.scores import get_score
from unigram import Unigram
from math import log
import tqdm


def bi_calc(words, pre_graph, follow_graph, route):
    for word in words:
        if word == '<BOS>':
            route[word] = (0.0, '<BOS>')
        else:
            if word in follow_graph:
                nodes = follow_graph[word]
            else:
                route[word] = (-100000, '<BOS>')
                continue
            route[word] = max((pre_graph[node][word] + route[node][0], node) for node in nodes)


class Bigram(Unigram):
    def __init__(self, uni_dict, bi_dict):
        # 一元前缀词典：lfreq, 词数：ltoal
        super().__init__(uni_dict)
        self.filename = bi_dict
        # 保存二元前缀词典
        self.bi_lfreq = {}
        # 生成二元词典
        self.gen_bi_pfdict()

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
                else:
                    self.bi_lfreq[word2][word1] = freq
                line = fp.readline()

    def log_p(self, words):
        """
        计算 log(w_1 | w_2)
        :param words: 二元元组，两个单词
        :return: 返回 log(w_1 | w_2)
        """
        assert len(words) == 2
        (w1, w2) = words
        p_w1 = 0.01 if w1 not in self.lfreq else self.lfreq[w1]
        p_w12 = 0.01 if w2 not in self.bi_lfreq or w1 not in self.bi_lfreq[w2] else self.bi_lfreq[w2][w1]
        p_w1 += 0.01
        p_w12 += 0.01
        return log(p_w12) - log(p_w1)

    def search(self, sentence):
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
        pre_graph = {}
        pre_graph['<BOS>'] = {}
        follow_graph = {}
        # 去掉<BOS>的第一个词
        for x in DAG[5]:
            pre_graph['<BOS>'][(5, x + 1)] = self.log_p(("<BOS>", sentence[5:x + 1]))
        # print(pre_graph['<BOS>'])
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
                pre_graph[(n, x + 1)] = temp
            n += 1

        words = list(pre_graph.keys())
        for pre in words:
            for word in pre_graph[pre].keys():  # 遍历pre_word的后一个词
                follow_graph[word] = follow_graph.get(word, list())
                follow_graph[word].append(pre)
        words.append('<EOS>')

        route = {}
        bi_calc(words, pre_graph, follow_graph, route)
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
        # print(sentence_words)
        return sentence_words

    def tokenize(self, data_file, target_file):
        """
        最终分词程序
        :param data_file: 待分词的文本
        :param target_file: 分词结果输入目标文本
        """
        with open(data_file) as f:
            lines = f.readlines()
            tf = open(target_file, 'w')
            for line in tqdm.tqdm(lines):
                segList = self.search(line)
                # print(segList)
                write_file(segList, tf)
            f.close()
            tf.close()


if __name__ == '__main__':
    bi = Bigram('../../data/dict.txt', '../../data/bi_dict.txt')
    # bi.search("19980101-01-001-004１２月３１日，中共中央总书记、国家主席江泽民发表１９９８年新年讲话《迈向充满希望的新世纪》。（新华社记者红光摄）")
    # bi.tokenize('../../data/199801_sent.txt', '../../data/seg_Bigram.txt')
    bi.tokenize('../../data/test_in.txt', '../../data/seg_test.txt')
    # print(get_score('../../data/199801_seg&pos.txt', '../../data/seg_Bigram.txt'))
