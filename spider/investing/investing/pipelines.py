# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv
import datetime

month_map = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
    'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
    'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
}


class InvestingPipeline(object):
    def process_item(self, item, spider):
        return item


class WriteCSVPipeline(object):
    def __init__(self):
        self.file = open('output.csv', 'w', newline='')
        self.csv = csv.writer(self.file)

    def _transform_time(self, raw_time):
        raw_time = str(raw_time)
        time = None
        if raw_time.find('ago') != -1:
            print(raw_time)
            time = datetime.datetime.now()-datetime.timedelta(hours=13)
        else:
            pieces = raw_time.replace(',', ' ').split()
            y = pieces[2]
            m = month_map[pieces[0]]
            d = pieces[1]
            time = datetime.datetime(year=int(y), month=int(m), day=int(d))
        return time.strftime("%y-%m-%d")

    def process_item(self, item, spider):
        company = str(item['company'])
        time = self._transform_time(item['time'])
        text = str(item['text'])
        row = [company, time, text]
        self.csv.writerow(row)
        return item

    def close_spider(self, spider):
        self.file.close()

