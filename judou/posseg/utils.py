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
    使用正则，根据传进来的句子识别日期等
    :param sentence:
    :return: 返回日期下标列表
    """
    # 得到词典所用的正则匹配串
    data_list = []
    for pattern in patterns:
        l = pattern.finditer(sentence)
        # 先用正则添加词典中
        for w in l:
            # 正则匹配到的下标
            (i, j) = w.span()
            # print((i,j))
            # 防止正则匹配过度泛化
            if i == 0 and j > 19:
                data_list.append((20, j))
                j = 19
            data_list.append((i, j))
    return data_list


def IdDate_all(sentence):
    """
    使用正则，返回具体字符串
    :param sentence: 传入的句子
    :return: 返回列表，四种匹配
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
            # 替换成功
            if sentence != old_sentence:
                tmp_pad_list.append(word)
        pad_list.append(tmp_pad_list)
    pad_dict = {'#': pad_list[0], '^': pad_list[1], '_': pad_list[2], '&': pad_list[3]}
    # print(pad_list)
    return sentence, pad_dict


def decode(words, pad_dict):
    """
    将用#覆盖的未登录词还原
    :param words: 覆盖后的句子
    :param words_cache: 覆盖前单词缓存
    :return: 无
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
    对数插值
    :param dic_list: 列表
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
    GoodTuring结合katz会回退平滑算法
    :param uni_dict: 一元词典
    :param uni_total: 一元词典总词数
    :param bi_dict: 二元词典
    :return: 返回n[r]表
    """
    # 计算n[r]表
    # 得到最大r
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
    根据数据集特点，特化处理，单独出来数据集开头的字符
    :param line: 待处理的句子
    :param words: 第一个单词列表
    :return: 删掉后的句子
    """
    date = date_pattern.match(line)
    print(date)
    # 只处理开头的
    if date and date.span()[0] == 0:
        words.append(str(date.group()))
        line = re.sub(date_str, '', line)
    return line


def is_date(sentence_seg):
    """
    判断一串字符是否能被正则识别
    :param sentence_seg: 字符串
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
    print(is_date("12月31日"))