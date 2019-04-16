import pandas as pd
import os
# from keras.preprocessing.text import Tokenizer
# from keras.preprocessing.sequence import pad_sequences
from data_util import MAX_FEATURES,MAX_NEWS_LEN,MAX_NEWS_NUM
from bert_serving.client import BertClient


class BasicEncoder(object):
    def embedding(self, newslist):
        pass


class BertEncoder(BasicEncoder):
    def __init__(self):
        self.bc = BertClient()
        super.__init__()

    def embedding(self, news_list):
        self.bc.encode(news_list)


class GloveEncoder(BasicEncoder):
    pass


class ElmoEncode(BasicEncoder):
    pass


