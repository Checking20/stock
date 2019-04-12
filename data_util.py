import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset
from sklearn.preprocessing import MinMaxScaler

# days taken into consideration for news
DATE_INTERVAL_NEWS = 3
# days taken into consideration for numerics
DATE_INTERVAL_NUM = 20
# the number of words in a piece of news taken into consideration
MAX_FEATURES = 20000
# max lenght of one pieces of news
MAX_LEN = 30
# max number of news taken into consideration per day
MAX_NEWS_NUM = 30

# normalize the input data to make RNN work better
def normalize(arr2d):
    arr2d = arr2d.astype('float64')
    n_arr2d = None
    '''## scaler according to row
       for j in range(arr2d.shape[1]):
       scaler = MinMaxScaler(copy=True, feature_range=(0, 1))
       values = arr2d[:,j]
       values = values.reshape(-1,1)
       scaler.fit(values)
       if n_arr2d is None:
           n_arr2d = scaler.transform(values)
       else:
           n_arr2d = np.concatenate((n_arr2d,scaler.transform(values)),axis=1)
    '''      
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
            n_arr2d = np.concatenate((n_arr2d,scaler.transform(values)),axis=1)
    return n_arr2d

# generate structed textual input with sliding_window
# the window update by real day
def get_x_seqs_by_sw(data_dict, days=DATE_INTERVAL_NEWS):
    range_dict = dict()
    mindate = pd.Timestamp(2100,1,1)
    maxdate = pd.Timestamp(2000,1,1)
    for date in data_dict.keys():
        mindate = min(mindate, date)
        maxdate = max(maxdate, date)
    maxdate = maxdate+DateOffset(days=1)
    mindate = mindate+DateOffset(days=days)
    for c_date in pd.date_range(start=mindate, end=maxdate):
        range_dict[c_date] = list()
        for p_date in pd.date_range(end=c_date-DateOffset(days=days), periods=days):
            if p_date in data_dict:
                range_dict[c_date].append(np.array(data_dict[p_date]))
            else:
                range_dict[c_date].append(np.zeros((MAX_NEWS_NUM,MAX_LEN)))
        range_dict[c_date] = np.array(range_dict[c_date],dtype='int32')
    return range_dict

# generate structed numerical input with sliding window
# the window update by market day
def get_x_by_sw(data_set,size=DATE_INTERVAL_NUM):
    data_dict = dict()
    left = right = 0 #including left but not right
    for i in range(len(data_set)):
        if right>=left+size:
            data_dict[data_set[right][0]] = \
            normalize(np.delete(data_set[left:right],[0,4],axis=1)) #remove 'Date' and 'Close'
            left += 1
        right += 1
    return data_dict

def get_y(data_set):
    data_dict =dict()
    len9 = len(data_set)
    for i in range(len9):
        toward = i
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

def match_xy(x_dict,y_dict):
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

# match x(news) with y
def get_xy_txt(news_data, num_data):
    x_dict = get_x_seqs_by_sw(news_data)
    y_dict = get_y(num_data)
    return match_xy(x_dict,y_dict)

# match x(numerics) with y
def get_xy(data_set):
    x_dict = get_x_by_sw(data_set)
    y_dict = get_y(data_set)
    return match_xy(x_dict,y_dict)