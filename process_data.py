import os
import re
import embedding as emb
import pandas as pd

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

        n_train.to_csv(target_dir+'news_train', index=False)
        n_val.to_csv(target_dir + 'news_val', index=False)
        n_test.to_csv(target_dir + 'news_test', index=False)

        p_train.to_csv(target_dir + 'prices_train', index=False)
        p_val.to_csv(target_dir + 'prices_val', index=False)
        p_test.to_csv(target_dir + 'prices_test', index=False)


def _load_data(code):
    code_dir = DATA_DIR+code+'/'

    if not os.path.exists(code_dir+'news_train_embedded'):
        pass
    #p_train = pd.read_csv()
    #p_val = pd.read_csv()
    #p_test = pd.read_csv()

    if os.path.exists(code_dir+'prices_train_normalized'):
        pass
    #n_train = pd.read_csv()
    #n_val = pd.read_csv()
    #n_test = pd.read_csv()


def load_data(codes):
    for code in codes:
        _load_data(code)


if __name__ == '__main__':
    pairs_dict = find_pairs()
    # div_data_by_date(pairs_dict, '2018-9-1', '2019-1-1')
    load_data(pairs_dict.keys())