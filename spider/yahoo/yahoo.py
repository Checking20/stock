#!/usr/bin/env python3
"""
Crawl daily price data from yahoo finance to generate raw data

Require "./input/news_reuters.csv"
==> "./input/finished.reuters" by calc_finished_ticker()
==> "./input/stockPrices_raw.json" by get get_stock_prices()
json structure:
         ticker
        /  |   \
    open close adjust ...
      /    |     \
   dates dates  dates ...
"""
import sys
import re
import os
import time
import random
import pandas as pd

# Credit: https://github.com/c0redumb/yahoo_quote_download/blob/master/yahoo_quote_download/yqd.py
from yqd import load_yahoo_quote


def get_stock_prices(code='^IXIC', start_date='20150101', end_date='20160101'):
    output = 'price/stockPrices_%s.csv'%(code)
    price = repeat_download(code, start_date, end_date)
    if price is not None:
        price.to_csv(output, index=False)
    else:
        print('the price data of %d can not be fetched now')


def repeat_download(ticker, start_date, end_date):
    # repeat download for N times
    repeat_times = 5
    for i in range(repeat_times):
        try:
            time.sleep(1+random.random())
            price_df = load_yahoo_quote(ticker, start_date, end_date, format_output='dataframe')
            # skip loop if data is not empty
            if price_df is not None:
                print(price_df.head())
                return price_df
        except Exception as e:
            print(e)
    return None


if __name__ == "__main__":
    start = '20120101'
    end = '20190301'
    get_stock_prices(code='^IXIC', start_date=start, end_date=end)
    get_stock_prices(code='AAPL', start_date=start, end_date=end)
    get_stock_prices(code='FB', start_date=start, end_date=end)
    get_stock_prices(code='MSFT', start_date=start, end_date=end)
    get_stock_prices(code='AMZN', start_date=start, end_date=end)
    get_stock_prices(code='GOOG', start_date=start, end_date=end)