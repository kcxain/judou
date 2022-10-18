# -*- coding: gbk -*-
from lab1.tokenizers.MM import MM
import re


class BMM(MM):
    def __init__(self, target_file='seg_BMM.txt'):
        super().__init__()
        self.target_file = target_file
