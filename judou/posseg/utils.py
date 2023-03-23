# -*- coding: gbk -*-
import math
import re
from math import log

from ..dict_reader.Vocab import Vocab

padding = ['#', '^', '_', '&']
date_str = '[0-9]*[-][0-9]*[-][0-9]{3}[-][0-9]{3}'
date_pattern = re.compile('[0-9]*[-][0-9]*[-][0-9]{3}[-][0-9]{3}')
v = Vocab()
patterns = v.get_pattern()


def IdDate(sentence):
    """
    ʹ�����򣬸��ݴ������ľ���ʶ�����ڵ�
    :param sentence:
    :return: ���������±��б�
    """
    # �õ��ʵ����õ�����ƥ�䴮
    data_list = []
    for pattern in patterns:
        l = pattern.finditer(sentence)
        # ����������Ӵʵ���
        for w in l:
            # ����ƥ�䵽���±�
            (i, j) = w.span()
            # print((i,j))
            # ��ֹ����ƥ����ȷ���
            if i == 0 and j > 19:
                data_list.append((20, j))
                j = 19
            data_list.append((i, j))
    return data_list


def IdDate_all(sentence):
    """
    ʹ�����򣬷��ؾ����ַ���
    :param sentence: ����ľ���
    :return: �����б�����ƥ��
    """
    pad_list = []
    i = 0
    for pattern in patterns:
        pad = padding[i]
        i += 1
        tmp = pattern.findall(sentence)
        # print(tmp)
        tmp_pad_list = []
        if tmp is None:
            pad_list.append(tmp_pad_list)
            continue
        for tuple_date in tmp:
            word = list(tuple_date)[0]
            if i == 2 and len(word) > 19:
                word = word[:19]
            old_sentence = sentence
            sentence = sentence.replace(word, pad, 1)
            # �滻�ɹ�
            if sentence != old_sentence:
                tmp_pad_list.append(word)
        pad_list.append(tmp_pad_list)
    pad_dict = {'#': pad_list[0], '^': pad_list[1], '_': pad_list[2], '&': pad_list[3]}
    # print(pad_list)
    return sentence, pad_dict


def decode(words, pad_dict):
    """
    ����#���ǵ�δ��¼�ʻ�ԭ
    :param words: ���Ǻ�ľ���
    :param words_cache: ����ǰ���ʻ���
    :return: ��
    """
    indexs = {'#': 0, '^': 0, '_': 0, '&': 0}
    for i in range(len(words)):
        if words[i] not in padding:
            continue
        pad = words[i]
        words[i] = pad_dict[pad][indexs[pad]]
        indexs[pad] += 1


def interpolation(dic_list):
    """
    ������ֵ
    :param dic_list: �б�
    :return:
    """
    nr = [i for i in dic_list if i != 0]
    r = [i + 1 for i in range(len(nr) - 1)]
    zr = []
    for j in range(len(r)):
        i = r[j - 1] if j > 0 else 0
        k = 2 * r[j] - i if j == len(r) - 1 else r[j + 1]
        zr_ = 2.0 * nr[j] / (k - i)
        zr.append(zr_)

    log_r = [math.log(i) for i in r]
    log_zr = [math.log(i) for i in zr]

    xy_cov = x_var = 0.0
    x_mean = sum(log_r) / len(log_r)
    y_mean = sum(log_zr) / len(log_zr)
    for (x, y) in zip(log_r, log_zr):
        xy_cov += (x - x_mean) * (y - y_mean)
        x_var += (x - x_mean) ** 2
    b = xy_cov / x_var if x_var != 0 else 0.0
    a = y_mean - b * x_mean
    for i in range(1, len(dic_list)):
        if dic_list[i] == 0:
            dic_list[i] = math.exp(a + b * log(i))


def good_tuning_smoothing(uni_dict, bi_dict):
    """
    GoodTuring���katz�����ƽ���㷨
    :param uni_dict: һԪ�ʵ�
    :param uni_total: һԪ�ʵ��ܴ���
    :param bi_dict: ��Ԫ�ʵ�
    :return: ����n[r]��
    """
    # ����n[r]��
    # �õ����r
    __max = 0
    for w2 in bi_dict:
        for w1 in bi_dict[w2]:
            __max = max(__max, bi_dict[w2][w1])
    bi_n = [0 for i in range(0, __max + 2)]
    # print(len(bi_n))
    # print(bi_n[20470])
    for w2 in bi_dict:
        for w1 in bi_dict[w2]:
            # print(bi_dict[w2][w1])
            bi_n[bi_dict[w2][w1]] += 1
    __max = 0
    for w in uni_dict:
        __max = max(__max, uni_dict[w])
    uni_n = [0 for i in range(0, __max + 2)]
    for w in uni_dict:
        uni_n[uni_dict[w]] += 1
    interpolation(uni_n)
    interpolation(bi_n)
    return uni_n, bi_n


def begging_number(line, words):
    """
    �������ݼ��ص㣬�ػ����������������ݼ���ͷ���ַ�
    :param line: ������ľ���
    :param words: ��һ�������б�
    :return: ɾ����ľ���
    """
    date = date_pattern.match(line)
    print(date)
    # ֻ����ͷ��
    if date and date.span()[0] == 0:
        words.append(str(date.group()))
        line = re.sub(date_str, '', line)
    return line


def is_date(sentence_seg):
    """
    �ж�һ���ַ��Ƿ��ܱ�����ʶ��
    :param sentence_seg: �ַ���
    :return: BOOL
    """
    for pattern in patterns:
        if pattern.fullmatch(sentence_seg):
            return True
    return False


def sentence_cut(sentence):
    for pattern in patterns:
        print(pattern.split(sentence))


if __name__ == '__main__':
    print(is_date("12��31��"))