# -*- coding: utf-8 -*-

from scrapy import Item, Field
from scrapy.loader.processors import *


class sybk(Item):


    mysql_spiders = ['sybk']
    mysql_tables = ['sybk']
    courseName = Field()
    title = Field()
    content = Field()
    url = Field()
    domain = Field()
    catFirst = Field()
    catSecond = Field()
    year = Field()
    catThird = Field()
