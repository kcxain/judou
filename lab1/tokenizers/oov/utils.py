# -*- coding: gbk -*-
from lab1.vocab.Vocab import Vocab


def IdDate(sentence):
    """
    使用正则，根据传进来的句子识别日期等
    :param sentence:
    :return: 返回日期下标列表
    """
    # 得到词典所用的正则匹配串
    v = Vocab()
    patterns = v.get_pattern()
    data_list = []
    for pattern in patterns:
        l = pattern.finditer(sentence)
        # 先用正则添加词典中
        for w in l:
            # 正则匹配到的下标
            (i, j) = w.span()
            # 防止正则匹配过度泛化
            if i == 0 and j > 19:
                data_list.append((20, j))
                j = 19
            data_list.append((i, j))
    return data_list
