import pandas as pd
import os
# from keras.preprocessing.text import Tokenizer
# from keras.preprocessing.sequence import pad_sequences
from data_util import MAX_FEATURES,MAX_NEWS_LEN,MAX_NEWS_NUM
from bert_serving.client import BertClient


class BasicEncoder(object):
    EMBEDDING_SIZE = 300
    def embedding(self, newslist):
        pass


class BertEncoder(BasicEncoder):
    EMBEDDING_SIZE = 768
    def __init__(self):
        self.bc = BertClient()

    def embedding(self, news_list):
        return self.bc.encode(news_list).tolist()


class GloveEncoder(BasicEncoder):
    pass


class ElmoEncode(BasicEncoder):
    pass


