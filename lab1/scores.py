# -*- coding: gbk -*-
CHECK_FILE = './data/199801_seg&pos.txt'
BMM_FILE = './data/seg_BMM.txt'
FMM_FILE = './data/seg_FMM.txt'


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


if __name__ == '__main__':
    BMM_right_num = get_check(CHECK_FILE, BMM_FILE)
    BMM_pre_num = get_num(BMM_FILE)
    FMM_right_num = get_check(CHECK_FILE, FMM_FILE)
    FMM_pre_num = get_num(FMM_FILE)
    CHECK_num = get_num(CHECK_FILE)

    f = open('./score.txt', 'w')
    BMM_P = float(BMM_right_num) / float(BMM_pre_num)
    BMM_R = float(BMM_right_num) / float(CHECK_num)

    FMM_P = float(FMM_right_num) / float(FMM_pre_num)
    FMM_R = float(FMM_right_num) / float(CHECK_num)
    f.write(f'FMM：\n准确率：{FMM_P}\n'
            f'召回率：{FMM_R}\n'
            f'F-评价：{2 * FMM_P * FMM_R / (FMM_R + FMM_P)}\n\n'
            f'BMM：\n准确率：{BMM_P}\n'
            f'召回率：{BMM_R}\n'
            f'F-评价：{2 * BMM_P * BMM_R / (BMM_R + BMM_P)}')
    f.close()

