import os, sys, re
# add two spider to current path
sys.path.append('yahoo')
sys.path.append('investing')
import yahooSpider as ys
from urllib import request
from bs4 import BeautifulSoup

start = '20120101'
end = '20190301'
equities_url = 'equities'
code_url = 'code'
pages = 1000

def get_prefixes():
    prefixes = []
    head = {}
    head['User-Agent'] = 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D)\
        AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19'
    list_url = 'https://www.investing.com/equities/StocksFilter?noconstruct=1&smlID=0&sid=&tabletype=price&index_id=20'
    list_req = request.Request(list_url, headers=head)
    list_resp = request.urlopen(list_req)

    list_soup = BeautifulSoup(list_resp.read(), "html.parser")
    for a in list_soup.find_all('a'):
        href = a.get('href')
        if href and href.find('/equities/') != -1:
            prefixes.append((a.text, href))
    return prefixes

def get_crawled_list(url):
    crawled_list = list()
    try:
        efile = open(url, 'r', newline='\n')
        for line in efile:
            crawled_list.append(line[:-1])
        efile.close()
    except FileNotFoundError:
        pass
    return crawled_list

def crawl_textural_data():
    prefixes = get_prefixes()
    crawled_set = set(get_crawled_list(equities_url))
    for (name, prefix) in prefixes[:1]:
        if name not in crawled_set:
            print('Create Scrapy Spider to crawl news data of \'%s\'' % (name))
            os.system('cd investing/ ;scrapy crawl newspider -a prefix=%s -a page=%d' % (prefix,pages))
            with open(equities_url, 'a') as file:
                file.writelines([name, '\n'])
            print('Crawled Successfully')
        else:
            print('news data of \'%s\' has been crawled' % (name))

def crawl_numerical_data():
    news_dir = 'data/news/'
    code_list = []
    for filename in os.listdir(news_dir):
        pattern = re.compile(r'news_([a-zA-Z]*).csv')
        code = re.match(pattern,filename).group(1)
        code_list.append(code)

    crawled_set = set(get_crawled_list(code_url))
    for code in code_list:
        if code not in crawled_set:
            print('Create Spider to crawl prices data of \'%s\'' % (code))
            ys.get_stock_prices(code=code, start_date=start, end_date=end)
            with open(code_url, 'a') as file:
                file.writelines([code, '\n'])
            print('Crawled Successfully')
        else:
            print('prices data of \'%s\' has been crawled' % (code))


if __name__ == "__main__":
    crawl_textural_data()
    crawl_numerical_data()











