# -*- coding: gbk -*-
CHECK_FILE = '../dict/origin_data_set/199801_seg&pos.txt'
BMM_FILE = '../dict/test_output/seg_BMM.txt'
FMM_FILE = '../dict/test_output/seg_FMM.txt'


def get_num(data_file):
    """
    得到某文件中分词数量
    :return: 文件中分词数量
    """
    f = open(data_file)
    s = f.read()
    return s.count('/')


def get_wordstr(line):
    """
    把文件中一句话分割为单词列表
    """
    words = []
    word_list = line.split()
    for word in word_list:
        # word.replace('[', '') 无法正常替换
        if word[0] == '[':
            new_word = word[1:]
            word = new_word
        word.replace(']', '')
        # print(word)
        w = word.split('/')
        words.append(w[0])
    return words


def word2inval(words):
    """
    将分词转化为对应位置的区间
    """
    inval = []
    start = 0
    for word in words:
        end = start + len(word)
        inval.append((start, end))
        start = end
    return inval


def get_check(test_file, data_file):
    """
    得到正确分词数量
    :return: 正确分词数量
    """
    tf = open(test_file)
    df = open(data_file)
    t_lines = tf.readlines()
    d_lines = df.readlines()
    # 分词个数
    count = 0
    for t_line, d_line in zip(t_lines, d_lines):
        t_words = get_wordstr(t_line)
        d_words = get_wordstr(d_line)
        # print(t_words)
        # print(d_words)
        t_inval = word2inval(t_words)
        d_inval = word2inval(d_words)
        # print(t_inval)
        # print(d_inval)
        # 由于不能使用集合求交集，所以这里考虑暴力枚举
        # 注意：由于我这里把词转换成了关于位置的元组表示（前后相同的单词的表示是不同的），所以求交集的办法是可行的
        for t in t_inval:
            for d in d_inval:
                if t == d:
                    count += 1
                    break
    return count


def get_score(check_file, test_file):
    """
    得到分数
    :param check_file: 正确分词结果
    :param test_file: 要计算的分词结果
    :return: (准确率, 召回率, F评价)
    """
    right_num = get_check(check_file, test_file)
    pre_num = get_num(test_file)
    check_num = get_num(check_file)
    P = float(right_num) / float(pre_num)
    R = float(right_num) / float(check_num)
    F = 2 * P * R / (R + P)
    return P, R, F


if __name__ == '__main__':
    print(get_score('../dict/origin_data_set/199801_seg&pos.txt', '../dict/test_output/seg_BMM.txt'))
    print(get_score('../dict/origin_data_set/199801_seg&pos.txt', '../dict/test_output/seg_FMM.txt'))
