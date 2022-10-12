# -*- coding: gbk -*-
data_file = '../data/199801_seg&pos.txt'
target_file = '../data/dict.txt'

# 数字串统一为<numbers>
pad = '<numbers>'
d = dict()


# 按值升序排序
def get_sorted_list(dict_in, reverse=False):
    return sorted(dict_in.items(), key=lambda x: x[1], reverse=reverse)


with open(data_file, encoding='gbk') as f:
    lines = f.readlines()
    # 按空格分割
    for line in lines:
        line.replace(']', '')
        line.replace('[', '')
        word_list = line.split()
        for word in word_list:
            # print(word)
            w = word.split('/')
            single_word = w[0]
            if single_word not in d:
                d[single_word] = 1
            else:
                d[single_word] += 1
    f.close()

with open(target_file, 'w', encoding='gbk') as f:
    words = get_sorted_list(d)
    for word in words:
        f.write(word[0])
        f.write(' ')
        f.write(str(word[1]))
        f.write('\n')
    f.close()
