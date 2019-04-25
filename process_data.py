import os,re,json
from embedding import BertEncoder
import pandas as pd
import numpy as np
from data_util import get_xxy, get_cluster_by_day, pad_or_truncate

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
                    filesize = os.path.getsize(NEWS_DIR+'news_%s.csv'%code)
                    pair_dict[code] = (NEWS_DIR+'news_%s.csv'%code, NUM_DIR+'stockPrices_%s.csv'%code)

    return pair_dict


# divide data into train_set,val_set,test_set
def _div_data(df, dateBound1, dateBound2, after):

    date_str = 'Date'
    if date_str not in df.columns.values:
        date_str = 'date'
    df[date_str] = pd.to_datetime(df[date_str])
    df.sort_values(date_str, inplace=True)

    test = df[df[date_str] >= dateBound2]
    tmp = df[df[date_str] < dateBound2]
    tmp = tmp[tmp[date_str] >= after]
    val = tmp[tmp[date_str] >= dateBound1]
    train = tmp[tmp[date_str] < dateBound1]
    return train, val, test


def div_data_by_date(pair_dict, bound1, bound2, after='2014-01-01'):
    assert isinstance(bound1, str)
    assert isinstance(bound2, str)

    dateBound1 = pd.Timestamp(bound1)
    dateBound2 = pd.Timestamp(bound2)
    after = pd.Timestamp(after)


    for item in pair_dict.items():
        code = item[0]
        news_df = pd.read_csv(item[1][0])
        prices_df = pd.read_csv(item[1][1])
        n_train, n_val, n_test = _div_data(news_df, dateBound1, dateBound2, after)
        p_train, p_val, p_test = _div_data(prices_df, dateBound1, dateBound2, after)

        target_dir = DATA_DIR+code+'/'
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(target_dir, exist_ok=True)

        n_train.to_csv(target_dir + 'news_train.csv', index=False)
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

    for (key, value) in ntrain.items():
        train[key] = bertEncoder.embedding(value)

    for (key, value) in nval.items():
        val[key] = bertEncoder.embedding(value)

    for (key, value) in ntest.items():
        test[key] = bertEncoder.embedding(value)

    with open(code_dir + 'wv_train.json', 'w') as f:
        json.dump(train, f)

    with open(code_dir + 'wv_val.json', 'w') as f:
        json.dump(val, f)

    with open(code_dir + 'wv_test.json', 'w') as f:
        json.dump(test, f)


def news_to_wvc(codes):
    for code in codes:
        _news_to_wvc_by_code(code)


def _load_data_by_code(code):
    code_dir = DATA_DIR+code+'/'

    data_dict = dict()

    p_train = pd.read_csv(code_dir+'prices_train.csv')
    p_val = pd.read_csv(code_dir+'prices_val.csv')
    p_test = pd.read_csv(code_dir+'prices_test.csv')

    p_train['Date'] = pd.to_datetime(p_train['Date'])
    p_val['Date'] = pd.to_datetime(p_val['Date'])
    p_test['Date'] = pd.to_datetime(p_test['Date'])

    with open(code_dir + 'wv_train.json', 'r') as f:
        n_train = json.load(f)

    with open(code_dir + 'wv_val.json', 'r') as f:
        n_val = json.load(f)

    with open(code_dir + 'wv_test.json', 'r') as f:
        n_test = json.load(f)

    n_train = pad_or_truncate(n_train, filler=np.zeros(BertEncoder.EMBEDDING_SIZE))
    n_val = pad_or_truncate(n_val, filler=np.zeros(BertEncoder.EMBEDDING_SIZE))
    n_test = pad_or_truncate(n_test, filler=np.zeros(BertEncoder.EMBEDDING_SIZE))

    data_dict['train'] = get_xxy(n_train, p_train.values)
    data_dict['val'] = get_xxy(n_val, p_val.values)
    data_dict['test'] = get_xxy(n_test, p_test.values)

    print('data of %s is loaded'%(code))
    return data_dict


def load_data(codes):
    data_dict = dict()
    for code in codes:
        data_dict[code] = _load_data_by_code(code)
    return data_dict


def get_rank_of_size():
    pairs_dict = find_pairs()
    alist = []
    for key in pairs_dict:
        code = key
        size = os.path.getsize(pairs_dict[key][0])
        alist.append((code,size))
    alist.sort(key=lambda x:-x[1])
    alist = [code for (code,size) in alist]
    return alist


if __name__ == '__main__':
    # get_rank_of_size()
    pairs_dict = find_pairs()
    # div_data_by_date(pairs_dict, '2018-9-1', '2019-1-1')
    # news_to_wvc(list(pairs_dict.keys()))
    # load_data(pairs_dict.keys())
    # data_dict = load_data(['GOOGL'])
