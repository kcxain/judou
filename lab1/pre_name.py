data_file = 'data/origin_data_set/name.txt'
target_file = 'data/origin_data_set/name_pre.txt'
with open(data_file, encoding='gbk', errors='ignore') as f:
    tf = open(target_file, 'w', encoding='gbk')
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        if len(line) == 2 or len(line) == 3:
            tf.write(line[0] + '/' + '  ' + line[1] + '/' + '  ' + '\n')
        else:
            tf.write(line[:2] + '/' + '  ' + line[2:] + '/' + '  ' + '\n')
    tf.close()
    f.close()
