# -*- coding: utf-8 -*-
import scrapy
from investing.items import PieceOfNews


class NewspiderSpider(scrapy.Spider):

    name = 'newspider'
    allowed_domains = ['investing.com']

    # add additional parameters
    def __init__(self, target_prefix=None, page=100, *args, **kwargs):
        super(NewspiderSpider, self).__init__(*args, **kwargs)
        if target_prefix is None:
            target_prefix = '/equities/google-inc-news/'
        target_url = 'https//www.investing.com' + target_prefix
        self.start_urls = []
        for i in range(page):
            self.start_urls.append(target_url+str(i+1))

    # start_urls = ['https://www.investing.com/equities/microsoft-corp-news/%d'%(i+1) for i in range(360)]
    # start_urls = ['https://www.investing.com/equities/amazon-com-inc-news/%d' % (i + 1) for i in range(643)]
    # start_urls = ['https://www.investing.com/equities/google-inc-news/%d' % (i + 1) for i in range(600)]
    # start_urls = ['https://www.investing.com/equities/facebook-inc-news/%d' % (i + 1) for i in range(786)]

    # start_urls = ['https://www.investing.com/equities/apple-computer-inc-news/%d' % (i + 1) for i in range(778)]

    def parse(self, response):
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
