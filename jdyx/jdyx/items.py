# -*- coding: utf-8 -*-

from scrapy import Item, Field
from scrapy.loader.processors import *


class jdyx(Item):
    mysql_spiders = ['jdyx']
    mysql_tables = ['jdyx']

    catFirst = Field()
    catSecond = Field()
    catThird = Field()
    catFourth = Field()

    title = Field()
    content = Field()
    img = Field()
    price = Field()
    publishing_house = Field()

    url = Field()
    domain = Field()
