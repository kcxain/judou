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
    # �뽫�˱����޸�Ϊ�������ļ�·��
    source_file = '../judou/test.txt'

    # �뽫�˱����޸�Ϊ�ִ��ļ�����·��
    target_file = './seg_LM.txt'

    # ��ȡ��ע��������Ӧ����������Ӧ����

    # ����һԪ�ķ�
    # test_Unigram(source_file, target_file)

    # ���Զ�Ԫ�ķ�
    # test_Bigram(source_file, target_file)

    # ����HMM
    # test_HMM(source_file, target_file)

    # ���Զ�Ԫ�ķ���HMM�ں�
    test_Bigram_hmm(source_file, target_file)
