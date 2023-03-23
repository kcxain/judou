# -*- coding: gbk -*-
CHECK_FILE = '../dict/origin_data_set/199801_seg&pos.txt'
BMM_FILE = '../dict/test_output/seg_BMM.txt'
FMM_FILE = '../dict/test_output/seg_FMM.txt'


def get_num(data_file):
    """
    �õ�ĳ�ļ��зִ�����
    :return: �ļ��зִ�����
    """
    f = open(data_file)
    s = f.read()
    return s.count('/')


def get_wordstr(line):
    """
    ���ļ���һ�仰�ָ�Ϊ�����б�
    """
    words = []
    word_list = line.split()
    for word in word_list:
        # word.replace('[', '') �޷������滻
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
    ���ִ�ת��Ϊ��Ӧλ�õ�����
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
    �õ���ȷ�ִ�����
    :return: ��ȷ�ִ�����
    """
    tf = open(test_file)
    df = open(data_file)
    t_lines = tf.readlines()
    d_lines = df.readlines()
    # �ִʸ���
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
        # ���ڲ���ʹ�ü����󽻼����������￼�Ǳ���ö��
        # ע�⣺����������Ѵ�ת�����˹���λ�õ�Ԫ���ʾ��ǰ����ͬ�ĵ��ʵı�ʾ�ǲ�ͬ�ģ��������󽻼��İ취�ǿ��е�
        for t in t_inval:
            for d in d_inval:
                if t == d:
                    count += 1
                    break
    return count


def get_score(check_file, test_file):
    """
    �õ�����
    :param check_file: ��ȷ�ִʽ��
    :param test_file: Ҫ����ķִʽ��
    :return: (׼ȷ��, �ٻ���, F����)
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
