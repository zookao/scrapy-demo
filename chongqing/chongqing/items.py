# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ChongqingItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    keywords = scrapy.Field()
    description = scrapy.Field()
    content = scrapy.Field()
    screenshot = scrapy.Field()
    date = scrapy.Field()
    images = scrapy.Field() #不入库
    files = scrapy.Field() #不入库
    pass
