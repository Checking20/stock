# -*- coding: utf-8 -*-
import scrapy
from investing.items import PieceOfNews


class NewspiderSpider(scrapy.Spider):
    name = 'newspider'
    allowed_domains = ['investing.com']
    start_urls = ['https://www.investing.com/equities/amazon-com-inc-news/%d'%(i+1) for i in range(641)]

    def parse(self, response):
        company = response.xpath('//div[@class="instrumentHead"]/h1/text()').extract()[0].replace('\t', '')
        for article in response.xpath('//div[@class="mediumTitle1"]/article/div[@class="textDiv"]'):
            try:
                text = article.xpath('a/text()').extract()[0].replace('\xa0', ' ')
                time = article.xpath('.//span[@class="date"]/text()').extract()[0].replace('\xa0-\xa0', '')
                piece = PieceOfNews()
                piece['company'] = company
                piece['text'] = text
                piece['time'] = time
                yield piece
            except Exception:
                with open('exception', 'a') as file:
                    file.write("There is a new exception")
