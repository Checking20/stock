import os
import re
from embedding as BertEncoder
import pandas as pd
from data_util import get_xxy, get_cluster_by_day

NEWS_DIR = "data2/news/"
NUM_DIR = "data2/prices/"
DATA_DIR = "data2/data/"


# find the codes with both news data and prices data
def find_pairs():
    pair_dict = dict()
    code_set = set()
    pattern1 = re.compile(r'news_([A-Z]*).csv')
    pattern2 = re.compile(r'stockPrices_([A-Z]*).csv')
    # Traversal news directory
    for _, _, files in os.walk(NEWS_DIR,topdown=False):
        for filename in files:
            matchObj = re.match(pattern1, filename)
            if matchObj is not None:
                code_set.add(matchObj.group(1))

    # Traversal prices directory
    for _, _, files in os.walk(NUM_DIR,topdown=False):
        for filename in files:
            matchObj = re.match(pattern2, filename)
            if matchObj is not None:
                code = matchObj.group(1)
                if code in code_set:
                    pair_dict[code] = (NEWS_DIR+'news_%s.csv'%code, NUM_DIR+'stockPrices_%s.csv'%code)

    return pair_dict


# divide data into train_set,val_set,test_set
def _div_data(df, dateBound1, dateBound2):

    date_str = 'Date'
    if date_str not in df.columns.values:
        date_str = 'date'
    df[date_str] = pd.to_datetime(df[date_str])
    df.sort_values(date_str, inplace=True)

    test = df[df[date_str] >= dateBound2]
    tmp = df[df[date_str] < dateBound2]
    val = tmp[tmp[date_str] >= dateBound1]
    train = tmp[tmp[date_str] < dateBound1]
    return train, val, test


def div_data_by_date(pair_dict, bound1, bound2):
    assert isinstance(bound1, str)
    assert isinstance(bound2, str)

    dateBound1 = pd.Timestamp(bound1)
    dateBound2 = pd.Timestamp(bound2)


    for item in pair_dict.items():
        code = item[0]
        news_df = pd.read_csv(item[1][0])
        prices_df = pd.read_csv(item[1][1])
        n_train, n_val, n_test = _div_data(news_df, dateBound1, dateBound2)
        p_train, p_val, p_test = _div_data(prices_df, dateBound1, dateBound2)

        target_dir = DATA_DIR+code+'/'
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(target_dir, exist_ok=True)

        n_train.to_csv(target_dir+'news_train.csv', index=False)
        n_val.to_csv(target_dir + 'news_val.csv', index=False)
        n_test.to_csv(target_dir + 'news_test.csv', index=False)

        p_train.to_csv(target_dir + 'prices_train.csv', index=False)
        p_val.to_csv(target_dir + 'prices_val.csv', index=False)
        p_test.to_csv(target_dir + 'prices_test.csv', index=False)


# transfer news to word vector cluster
def _news_to_wvc_by_code(code):
    code_dir = DATA_DIR + code + '/'

    ntrain = pd.read_csv(code_dir+'news_train.csv')
    nval = pd.read_csv(code_dir+'news_val.csv')
    ntest = pd.read_csv(code_dir+'news_test.csv')

    ntrain['date'] = pd.to_datetime(ntrain['date'])
    nval['date'] = pd.to_datetime(nval['date'])
    ntest['date'] = pd.to_datetime(ntest['date'])

    ntrain = get_cluster_by_day(ntrain)
    nval = get_cluster_by_day(nval)
    ntest = get_cluster_by_day(ntest)

    train = dict()
    val = dict()
    test = dict()


    bertEncoder = BertEncoder()

    for (key,value) in ntrain.items():
        train[key] = bertEncoder.embedding(value)

    for (key,value) in nval.items():
        val[key] = bertEncoder.embedding(value)

    for (key,value) in ntest.items():
        test[key] = bertEncoder.embedding(value)










def news_to_wvc(codes):
    for code in codes:
        _news_to_wvc_by_code(code)


def _load_data_by_code(code):
    code_dir = DATA_DIR+code+'/'
    data_dict = dict()

    data_dict['ptrain'] = pd.read_csv(code_dir+'prices_train.csv')
    data_dict['pval'] = pd.read_csv(code_dir+'prices_val.csv')
    data_dict['ptest'] = pd.read_csv(code_dir+'prices_test.csv')

    data_dict['ntrain'] = pd.read_csv(code_dir+'news_train.csv')
    data_dict['nval'] = pd.read_csv(code_dir+'news_val.csv')
    data_dict['ntest'] = pd.read_csv(code_dir+'news_test.csv')

    return data_dict


def load_data(codes):
    data_dict = dict()
    for code in codes:
        data_dict[code] = _load_data_by_code(code)
    return data_dict


if __name__ == '__main__':
    pairs_dict = find_pairs()
    # div_data_by_date(pairs_dict, '2018-9-1', '2019-1-1')
    # load_data(pairs_dict.keys())
    news_to_wvc(pairs_dict.keys())
