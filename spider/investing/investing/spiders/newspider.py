# -*- coding: utf-8 -*-
import re
import scrapy
from investing.items import PieceOfNews


class NewspiderSpider(scrapy.Spider):
    name = 'newspider'
    allowed_domains = ['investing.com']

    # add additional parameters
    def __init__(self, prefix=None, page=10, *args, **kwargs):
        super(NewspiderSpider, self).__init__(*args, **kwargs)
        if prefix is None:
            prefix = '/equities/google-inc'
        page = int(page)
        target_url = 'https://www.investing.com%s-news/'%(prefix)
        self.fail_count = 0
        self.start_urls = [target_url + str(i+1) for i in range(page)]

    # overload the method 'start_requests'
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={'dont_redirect': True,'handle_httpstatus_list': [302, 406]})


    def parse(self, response):
        if response.status == 302 or response.status == 406:
            self.fail_count += 1
            print("current fail time is %d" % (self.fail_count))
            return
        title = response.xpath('//div[@class="instrumentHead"]/h1/text()').extract()[0].replace('\t', '')
        pattern = re.compile(r'(.*) \(([A-Z]*)\)')
        matchOj = re.match(pattern,title)
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
