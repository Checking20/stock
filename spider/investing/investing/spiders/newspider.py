# -*- coding: utf-8 -*-
import re
import scrapy
from investing.items import PieceOfNews


class NewspiderSpider(scrapy.Spider):
    name = 'newspider'
    allowed_domains = ['investing.com']

    # add additional parameters
    def __init__(self, prefix=None, min_page=50, max_page=1000, *args, **kwargs):
        super(NewspiderSpider, self).__init__(*args, **kwargs)
        if prefix is None:
            prefix = '/equities/google-inc'
        target_url = 'https://www.investing.com%s-news/'%(prefix)
        self.start_urls = [target_url]
        self.max_page = int(max_page)
        self.min_page = int(min_page)

    # overload the method 'start_requests'
    def start_requests(self):
        url = self.start_urls[0]
        yield scrapy.Request(url, callback=self.try_parse)


    def try_parse(self, response):
        info = response.xpath('//div[@class="sideDiv inlineblock text_align_lang_base_2"]/a/@title').extract()[0]
        pattern = re.compile(r'Show results [0-9]* to [0-9]* of ([0-9]*)')
        pages = int(re.match(pattern, info).group(1))//10
        # boundary: min_page,max_page
        pages = min(pages, self.max_page)
        if pages < self.min_page:
            return
        need_crawling_urls = [self.start_urls[0] + str(i+1) for i in range(pages)]
        for url in need_crawling_urls:
            yield scrapy.Request(url,
                                 meta={'dont_redirect': True, 'handle_httpstatus_list': [302]},
                                 callback=self.parse)


    def parse(self, response):
        # 302 and 406 means there is no useful data
        if response.status == 302:
            return
        title = response.xpath('//div[@class="instrumentHead"]/h1/text()').extract()[0].replace('\t', '')
        pattern = re.compile(r'(.*) \(([A-Z]*)\)')
        matchOj = re.match(pattern, title)
        for article in response.xpath('//div[@class="mediumTitle1"]/article/div[@class="textDiv"]'):
            try:
                text = article.xpath('a/text()').extract()[0].replace('\xa0', ' ').replace(',', ' ')
                time = article.xpath('.//span[@class="date"]/text()').extract()[0].replace('\xa0-\xa0', '')
                piece = PieceOfNews()
                piece['code'] = matchOj.group(2)
                piece['company'] = matchOj.group(1)
                piece['text'] = text
                piece['time'] = time
                yield piece
            except Exception:
                with open('exception', 'a') as file:
                    file.write("There is a new exception")
