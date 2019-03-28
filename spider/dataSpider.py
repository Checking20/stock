import os, sys, re
# add two spider to current path
sys.path.append('yahoo')
sys.path.append('investing')
# import yahooSpider as ys
from urllib import request
from bs4 import BeautifulSoup

start = '20120101'
end = '20190301'
def _get_prefixes():
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
            prefixes.append(href)
    return prefixes

if __name__ == "__main__":
    os.system('scrapy crawl newspider')








