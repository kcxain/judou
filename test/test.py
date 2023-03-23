# -*- coding: gbk -*-
import sys
sys.path.append("../")
from judou.posseg import mm, ngram, hmm

Unigram = ngram.Unigram
Bigram = ngram.Bigram
HMM = hmm.model

def test_Unigram(source_file='./test.txt', target_file='./seg_LM.txt'):
    d1 = Unigram('./data/dict/uni_dict.txt')
    d1.tokenize(source_file, target_file)


def test_Bigram(source_file='./test.txt', target_file='./seg_LM.txt'):
    bi = Bigram('./data/dict/uni_dict.txt', './data/dict/bi_dict.txt', './data/hmm_model/hmm_model.pkl')
    bi.tokenize(source_file, target_file)


def test_HMM(source_file='./test.txt', target_file='./seg_LM.txt'):
    hmm = HMM('./data/hmm_model/hmm_model.pkl')
    hmm.tokenizer(source_file, target_file)


def test_Bigram_hmm(source_file='./test.txt', target_file='./seg_LM.txt'):
    bi = Bigram('./data/dict/uni_dict.txt', './data/dict/bi_dict.txt', './data/hmm_model/hmm_model.pkl')
    bi.tokenize(source_file, target_file, hmm_oov=True)


if __name__ == '__main__':
    # 请将此变量修改为待测试文件路径
    source_file = '../judou/test.txt'

    # 请将此变量修改为分词文件保存路径
    target_file = './seg_LM.txt'

    # 清取消注释运行相应代码运行相应内容

    # 测试一元文法
    # test_Unigram(source_file, target_file)

    # 测试二元文法
    # test_Bigram(source_file, target_file)

    # 测试HMM
    # test_HMM(source_file, target_file)

    # 测试二元文法与HMM融合
    test_Bigram_hmm(source_file, target_file)
