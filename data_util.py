import pandas as pd
import numpy as np
import random
from scipy import sparse
from pandas.tseries.offsets import DateOffset
from sklearn.preprocessing import MinMaxScaler

# days taken into consideration for news
DATE_INTERVAL_NEWS = 7
# days taken into consideration for numerics
DATE_INTERVAL_NUM = 20
# the number of words in a piece of news taken into consideration
MAX_FEATURES = 20000
# max length of one pieces of news
MAX_NEWS_LEN = 40
# max number of news taken into consideration per day
MAX_NEWS_NUM = 50
# the length of embedding vectors
EMBEDDING_SIZE = 768


# change the dataframe into dict
# map: pd.Timestamp->news_group
def get_cluster_by_day(news_df,is_pair=False):
    news_group_dict = dict()
    for index, row in news_df.iterrows():
        # transfer pd.Timestamp into str
        date = str(row['date'].date())
        if date not in news_group_dict:
            news_group_dict[date] = list()
        if is_pair:
            news_group_dict[date].append(row['company']+'|||'+row['text'])
        else:
            news_group_dict[date].append(row['text'])

    return news_group_dict


def pad_or_truncate(raw_dict, filler=''):
    data_dict = dict()
    for key in raw_dict:
        blank = MAX_NEWS_NUM-len(raw_dict[key])
        if blank >= 0:
            for _ in range(blank):
                raw_dict[key].append(filler)
        else:
            for _ in range(-blank):
                raw_dict[key].pop()
        data_dict[pd.Timestamp(key)] = np.array(raw_dict[key])
    return data_dict


# normalize the input data to make RNN work better
def normalize(arr2d):
    arr2d = arr2d.astype('float64')
    n_arr2d = None
    # divide into two groups: prices(Open,Low,High,adjClose) and volume
    # then normalize them respectively
    a_num = arr2d.shape[1]
    p_scaler = MinMaxScaler(copy=True, feature_range=(0, 1))
    p_values = arr2d[:,0:a_num-1].reshape(-1,1)
    p_scaler.fit(p_values)
    v_scaler = MinMaxScaler(copy=True, feature_range=(0, 1))
    v_values = arr2d[:,a_num-1].reshape(-1,1)
    v_scaler.fit(v_values)
    for j in range(a_num):
        scaler = p_scaler
        if j == a_num-1:
            scaler = v_scaler
        values = arr2d[:,j]
        values = values.reshape(-1,1)
        if n_arr2d is None:
            n_arr2d = scaler.transform(values)
        else:
            n_arr2d = np.concatenate((n_arr2d, scaler.transform(values)), axis=1)
    return n_arr2d


# generate structed textual input with sliding_window
# the window update by real day
def get_x_seqs_by_sw(data_dict, days=DATE_INTERVAL_NEWS):
    range_dict = dict()
    mindate = pd.Timestamp(2100,1,1)
    maxdate = pd.Timestamp(2000,1,1)
    shape = None
    for date in data_dict.keys():
        if shape is None:
            shape = data_dict[date].shape
        mindate = min(mindate, date)
        maxdate = max(maxdate, date)
    maxdate = maxdate+DateOffset(days=1)
    mindate = mindate+DateOffset(days=days)
    for c_date in pd.date_range(start=mindate, end=maxdate):
        range_dict[c_date] = list()
        for p_date in pd.date_range(start=c_date-DateOffset(days=days), periods=days):
            if p_date in data_dict:
                range_dict[c_date].append(sparse.csr_matrix(np.array(data_dict[p_date])))
            else:
                range_dict[c_date].append(sparse.csr_matrix(np.zeros(shape=shape)))
        range_dict[c_date] = np.array(range_dict[c_date])
    return range_dict


# generate structed numerical input with sliding window
# the window update by market day
def get_x_by_sw(data_set, size=DATE_INTERVAL_NUM):
    data_dict = dict()
    left = right = 0 #including left but not right
    for i in range(len(data_set)):
        if right>=left+size:
            data_dict[data_set[right][0]] = \
            normalize(np.delete(data_set[left:right], [0,4], axis=1)) #remove 'Date' and 'Close'
            left += 1
        right += 1
    return data_dict


def get_y(data_set):
    data_dict =dict()
    len9 = len(data_set)
    for i in range(len9):
        toward = i+6
        forward = i-1
        if toward<len9 and forward>0:
            # How to define the change rate?
            # Now set rate = open_price[1]/open_prices[i-1]-1
            rate = data_set[toward][1]/data_set[forward][1]-1
            if rate <=0:
                data_dict[data_set[i][0]] = [1,0]
            else:
                data_dict[data_set[i][0]] = [0,1]
    return data_dict


def match_xy(x_dict, y_dict):
    x_list = list()
    y_list = list()
    # use keys(date) to match X and Y
    for key in x_dict.keys():
        if key in y_dict:
            x_list.append(x_dict[key])
            y_list.append(y_dict[key])
    x_arr = np.array(x_list)
    y_arr = np.array(y_list)
    return (x_arr,y_arr)


def match_xxy(x1_dict, x2_dict, y_dict):
    x1_list = list()
    x2_list = list()
    y_list = list()
    for key in x1_dict.keys():
        b1 = key in x2_dict
        b2 = key in y_dict
        if b1 and b2:
            x1_list.append(x1_dict[key])
            x2_list.append(x2_dict[key])
            y_list.append(y_dict[key])
    x1_arr = np.array(x1_list)
    x2_arr = np.array(x2_list)
    y_arr = np.array(y_list)
    return (x1_arr, x2_arr, y_arr)


# match x(news) with y
def get_xy_txt(news_data, num_data):
    x_dict = get_x_seqs_by_sw(news_data)
    y_dict = get_y(num_data)
    return match_xy(x_dict, y_dict)


# match x(numerics) with y
def get_xy(num_data):
    x_dict = get_x_by_sw(num_data)
    y_dict = get_y(num_data)
    return match_xy(x_dict, y_dict)


#match x1(news) x2(numerics) with y
def get_xxy(news_data, num_data):
    x1_dict = get_x_seqs_by_sw(news_data)
    x2_dict = get_x_by_sw(num_data)
    y_dict = get_y(num_data)
    return match_xxy(x1_dict, x2_dict, y_dict)


def unpack_news_data(news_array):
    unp = []
    for subarray in news_array:
        unp.append([mt.toarray() for mt in subarray])
    unp = np.array(unp)
    # print(unp.shape)
    return unp


# data generator to generate the batchs of train data
def data_generator(batch_size, data_tuple, additional_function=lambda x:x):
    while True:
        data_len = data_tuple[0].shape[0]
        index_array = np.arange(data_len)
        np.random.shuffle(index_array)
        point = 0
        while point < data_tuple[0].shape[0]:
            cur_batch_ids = index_array[point:min(point+batch_size, data_len)]
            cur_batch_x = [data[cur_batch_ids] for data in data_tuple[:-1]]
            cur_batch_x[0] = additional_function(cur_batch_x[0])
            cur_batch_y = data_tuple[-1][cur_batch_ids]
            cur_batch_data = (cur_batch_x, cur_batch_y)
            point += batch_size
            yield cur_batch_data


