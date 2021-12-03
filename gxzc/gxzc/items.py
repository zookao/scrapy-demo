# -*- coding: utf-8 -*-

from scrapy import Item, Field
from scrapy.loader.processors import *


class gxzc(Item):


    mysql_spiders = ['jdyx']
    mysql_tables = ['jdyx']
    title = Field()
    content = Field()
    catFirst = Field()
    catSecond = Field()
    catThird = Field()
    url = Field()
    domain = Field()
