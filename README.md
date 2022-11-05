# HIT-NLP-Lab

哈工大 2022 秋季学期《自然语言处理》课程实验

## 实验一：汉语分词系统

项目结构：
```
├── data
|  ├── dict
|  |  ├── bi_dict.txt
|  |  └── dict.txt
|  ├── hmm_model
|  |  └── h.pkl
|  ├── origin_data_set
|  |  ├── 199801_seg&pos.txt
|  |  ├── 199801_sent.txt
|  |  ├── 199802.txt
|  |  ├── 199803.txt
|  |  ├── name.txt
|  |  └── name_pre.txt
|  ├── test_in.txt
|  └── test_output
|     ├── seg_Bigram.txt
|     ├── seg_Bigram_hmm.txt
|     ├── seg_BMM.txt
|     ├── seg_FMM.txt
|     ├── seg_HMM.txt
|     ├── seg_test.txt
|     ├── seg_test_hmm.txt
|     └── seg_Unigram.txt
├── pre_name.py
├── score.txt
├── scores.py
├── tokenizers
|  ├── fmm_bmm
|  |  ├── BMM.py
|  |  ├── FMM.py
|  |  ├── MM.py
|  |  └── TimeCost.txt
|  ├── hmm
|  |  ├── HMM.py
|  |  └── train.py
|  ├── ngram
|  |  ├── bigram.py
|  |  └── unigram.py
|  └── oov
|  |  └── utils.py
└── vocab
|  ├── Vocab.py
|  └── VocabData.py
```
- `data`
  - `origin_data_set`: 原始训练语料，包括人民日报1998年1、2、3月份语料和部分人名资源
  - `dict`: 根据原始预料训练出的**一元词典**和**二元词典**
  - `hmm_model`: 训练出的**HMM**参数
  - `test_output`: 各模型对人民日报1998年1月分词测试结果
- `vocab`
  - `Vocab.py`: 从语料库中处理生成一元/二元词典的程序（加入了正则匹配过滤）
  - `VocabData.py`：构建词典数据结构，支持插入和搜索操作。两个实现类，`VocabList`使用**列表**实现，`VocabSet`使用**哈希表**实现
- `tokenizers`
  - `fmm_bmm`
    - `BMM.py`：**反向最大匹配分词**实现，分词结果生成`seg_BMM.txt`文件
    - `FMM.py`：**正向最大匹配分词**实现，分词结果生成`seg_FMM.txt`文件
    - 此外，分词时还会记录分词所耗费的时间，结果保存在`TimeCost.txt`中
  - `hmm`
    - `train.py`: 训练HMM的**由字构词**状态分布，状态转移，和发射概率矩阵，并将训练好的模型保存
    - `HMM.py`: 使用**维特比算法**实现HMM的未登录词识别
  - `ngram`
    - `unigram`: **一元文法**实现
    - `bigram`: **二元文法**实现（可选择加入HMM识别未登录词模块）
  - `oov`
    - `utils.py`: 处理正则使用的功能函数，模型平滑算法等
- `scores.py`：对分词算法的结果进行评价，分别计算**准确率**，**召回率**和 **F-评价**