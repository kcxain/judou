# -*- coding: gbk -*-
from lab1.vocab.Vocab import Vocab

padding = ['#', '^', '_', '&']
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
