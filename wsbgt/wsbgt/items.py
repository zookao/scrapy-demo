# -*- coding: utf-8 -*-

from scrapy import Item, Field
from scrapy.loader.processors import *


class wsbgt(Item):
    
    
    mysql_spiders = ['wsbgt']
    mysql_tables = ['wsbgt']
    courseName = Field()
    title = Field()
    content = Field()
    url = Field()
    domain = Field()
    catFirst = Field()
    catSecond = Field()
    catThird = Field()
    