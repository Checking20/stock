import os
import re
import embedding as emb

NEWS_DIR = "data2/news/"
NUM_DIR = "data2/prices/"
OUTPUT_DIR = "data2/processed_news/"


# find the codes with both news data and prices data
def find_pairs():
    pair_list = []
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
                    pair_list.append((NEWS_DIR+'news_%s.csv'%code, NUM_DIR+'stockPrices_%s.csv'%code))

    return pair_list


if __name__ == '__main__':
    find_pairs()