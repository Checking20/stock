import pandas as pd
import numpy as np
import os
from pytorch_pretrained_bert import BasicTokenizer
from data_util import MAX_FEATURES,MAX_NEWS_LEN,MAX_NEWS_NUM
from bert_serving.client import BertClient


class BasicEncoder(object):
    EMBEDDING_SIZE = 300

    def encode(self, newslist):
        pass


class BertEncoder(BasicEncoder):
    EMBEDDING_SIZE = 768

    def __init__(self):
        self.bc = BertClient()

    def encode(self, news_list):
        return self.bc.encode(news_list).tolist()


class GloveEncoder(BasicEncoder):
    EMB_FILE = 'tool/GloVe/glove.42B.300d.txt'
    GLOVE_DICT = None

    def __init__(self):
        if GloveEncoder.GLOVE_DICT is None:
            def get_coefs(word, *arr):
                return word, np.asarray(arr, dtype='float32')
            print('loading GloVe file...')
            GloveEncoder.GLOVE_DICT = dict(get_coefs(*o.strip().split()) for o in open(GloveEncoder.EMB_FILE))
            print('GloVe data has been loaded')
        self.tokenizer = BasicTokenizer()

    def encode(self, newslist):
        sen_vec_list = []
        for news in newslist:
            words = self.tokenizer.tokenize(news)
            vec_list = []
            for word in words:
                vec = self.GLOVE_DICT.get(word)
                if vec is not None:
                    vec_list.append(vec)
            if len(vec_list) > 0:
                sen_vec = np.mean(np.array(vec_list), axis=0)
            else:
                sen_vec = np.zeros(GloveEncoder.EMBEDDING_SIZE)
            sen_vec_list.append(sen_vec.tolist())
        return sen_vec_list


class ElmoEncode(BasicEncoder):
    pass


