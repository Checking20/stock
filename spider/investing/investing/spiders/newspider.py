# -*- coding: utf-8 -*-
import scrapy
from investing.items import PieceOfNews


class NewspiderSpider(scrapy.Spider):

    name = 'newspider'
    allowed_domains = ['investing.com']

    # add additional parameters
    def __init__(self, prefix=None, page=1000, code='DEFAULT', *args, **kwargs):
        super(NewspiderSpider, self).__init__(*args, **kwargs)
        if prefix is None:
            prefix = '/equities/google-inc'
        page = int(page)
        target_url = 'https://www.investing.com%s-news/'%(prefix)
        self.start_urls = [target_url + str(i+1) for i in range(page)]

        self.code = code


    # overload the method 'start_requests'
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={'dont_redirect': True,'handle_httpstatus_list': [302]})

    def parse(self, response):
        if response.status == 302:
            return
        company = response.xpath('//div[@class="instrumentHead"]/h1/text()').extract()[0].replace('\t', '')
        for article in response.xpath('//div[@class="mediumTitle1"]/article/div[@class="textDiv"]'):
            try:
                text = article.xpath('a/text()').extract()[0].replace('\xa0', ' ').replace(',', ' ')
                time = article.xpath('.//span[@class="date"]/text()').extract()[0].replace('\xa0-\xa0', '')
                piece = PieceOfNews()
                piece['company'] = company
                piece['text'] = text
                piece['time'] = time
                yield piece
            except Exception:
                with open('exception', 'a') as file:
                    file.write("There is a new exception")
