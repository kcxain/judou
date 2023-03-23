# -*- coding: gbk -*-
from abc import abstractmethod

from .Vocab import Vocab


def init_vocab(datafile='../../data/dict/uni_dict.txt', datatype=list):
    """
    ��̬����������ָ��ĳ�����ݽṹ������ʼ���ʵ�
    :param datafile: �ʵ��ŵı����ļ�
    :param datatype: ָ�����ݽṹ
    :return: ����ָ�����ݽṹ���ɵĴʵ�
    """
    vocab_data = VocabData()
    if datatype == "list":
        vocab_data = VocabList()
    if datatype == "set":
        vocab_data = VocabSet()
    f = open(datafile, encoding='gbk')
    lines = f.readlines()
    for line in lines:
        if line is None:
            continue
        word = line.split('\t')[0]
        # ���ö�Ӧ���ݽṹ��add����
        vocab_data.add(word)
    f.close()
    return vocab_data


class VocabData:
    """
    �����ඨ���ֵ�洢�����ݽṹ
    """

    def __init__(self):
        self.vocab = Vocab()
        self.maxlen = 0

    def maxLen(self):
        """
        :return:�ʵ������ʵĳ���
        """
        return self.maxlen

    @abstractmethod
    def __contains__(self, item):
        """
        ��д__contains__���������ڲ��Ҵʵ�
        :param item: Ҫ���ҵ��ַ���
        :return: BOOL���Ƿ����
        """
        pass

    @abstractmethod
    def add(self, item):
        """
        ��ʵ����Ԫ��
        :param item: Ԫ��
        :return: None
        """
        pass


class VocabList(VocabData):
    """
    ʹ��Python��list�洢�ʵ䣬��Ӧ��3.2
    """

    def __init__(self):
        super(VocabList, self).__init__()
        self.dict = list()

    def __contains__(self, item):
        return self.dict.__contains__(item)

    def add(self, item):
        # print(item)
        self.dict.append(item)
        # ά�����ִʳ���
        self.maxlen = max(self.maxlen, len(item))

    def __repr__(self):
        return self.dict.__repr__()

    def __len__(self):
        return len(self.dict)


class VocabSet(VocabData):
    """
    ��ϣ��洢�ʵ䣬������
    """

    def __init__(self, size=30000):
        super(VocabSet, self).__init__()
        self._size = size
        # Ԫ�ظ���
        self._filled = 0
        # ���Ա��׵�ַ
        self._element = [[] for _ in range(size)]

    def _hash_function(self, value):
        """
        ��ϣ����
        :param value:
        :return: hash(value)
        """
        return hash(value) % self._size

    def _contains(self, value):
        """
        :return: ���ض�Ӧ���Ա���Ԫ�ظ���������������򷵻�-1
        """
        for i, e in enumerate(self._element[self._hash_function(value)]):
            if value == e:
                return i
        return -1

    def contains(self, value):
        """
        :return: Ԫ�ش����򷵻�True,���򷵻�False
        """
        return self._contains(value) >= 0

    def add(self, value):
        """
        ���Ԫ��
        """
        self._filled += 1
        self.maxlen = max(self.maxlen, len(value))
        # print(value)
        self._element[self._hash_function(value)].append(value)
        # self._resize()

    def delete(self, value):
        """
        ɾ��Ԫ��
        """
        index = self._contains(value)
        if index >= 0:
            self._filled -= 1
            self._element[self._hash_function(value)].pop(index)
            self._resize()

    def _resize(self):
        """
        ��������ɢ�б�
        """
        # ���װ������
        RESIZE_FACTOR_UP = 1 / 2
        # ���װ������
        RESIZE_FACTOR_DOWN = 1 / 3
        # ��С��С
        MIN_SIZE = 1000
        # װ������
        capacity_ratio = float(self._filled) / self._size
        # װ������̫�ͣ�����
        if capacity_ratio < RESIZE_FACTOR_DOWN and self._size / 2 >= MIN_SIZE:
            self._create_resized_array(self._size / 2)
        # װ�����ӹ��ߣ�������size�����ͳ�ͻ����
        if capacity_ratio > RESIZE_FACTOR_UP:
            self._create_resized_array(self._size * 2)

    def _create_resized_array(self, new_size):
        """
        ����size,���½���ɢ�б�
        """
        new_element_array = [[] for _ in range(int(new_size))]
        self._size = len(new_element_array)
        for l in self._element:
            for e in l:
                new_element_array[self._hash_function(e)].append(e)
        self._element = new_element_array

    def __iter__(self):
        for l in self._element:
            if l:
                for e in l:
                    yield e
        raise StopIteration()

    def __repr__(self):
        res = list()
        for l in self._element:
            if l:
                for e in l:
                    res += e
        return res

    def __contains__(self, item):
        return self.contains(item)
