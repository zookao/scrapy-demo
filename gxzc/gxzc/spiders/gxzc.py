# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
from ..items import *

from scrapy_splash import SplashRequest


class GxzcSpider(RedisSpider):
    name = 'jdyx'
    allowed_domains = ['www.gx211.com',]
    custom_settings = {
        "MYSQL_HOST": "mysql",
        "MYSQL_PORT": 3306,
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "root",
        "MYSQL_DATABASE": "gerapy",

        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS": 2,

        "DOWNLOADER_MIDDLEWARES": {
            # 'jdyx.middlewares.RandomUserAgentMiddlware': 333,
            # "gerapy.downloadermiddlewares.pyppeteer.PyppeteerMiddleware": 601,
            "scrapy_splash.SplashCookiesMiddleware": 723,
            "scrapy_splash.SplashMiddleware": 725,
            "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810
        },

        "SPIDER_MIDDLEWARES": {
            "scrapy_splash.SplashDeduplicateArgsMiddleware": 100
        },

        "SPLASH_URL": 'http://splash:8050',

        "ITEM_PIPELINES": {
            "gerapy.pipelines.MySQLPipeline": 300
        },

        "REDIS_HOST": "redis",
        "REDIS_PARAMS": {
            "password": "caozongchao",
        },
        "REDIS_PORT": 6379,

        "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
        "SCHEDULER_QUEUE_CLASS": "scrapy_redis.queue.SpiderPriorityQueue",
        "DUPEFILTER_CLASS": "scrapy_redis.dupefilter.RFPDupeFilter",
        "SCHEDULER_PERSIST": True,

        # "DEFAULT_REQUEST_HEADERS": {
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        # }
    }
    # redis_key = 'jdyx:start_urls'

    def start_requests(self):
        l = [52,48,87,73,90,92,93,152,187,231,284,287,289,290,291,292,328,359,418,419,420,421,508,532,606,623,830,868,869,871,873,874,875,876,886,923,924,926,1004,1050,1071,1195,1226,1388,1570,1602,1603,1869,1981,2066,2184,2190,2305,2306,2307,2308,2309,2310,2311,2312,2399,2489,2557,2609]
        for i in l:
            _url = 'http://www.gx211.com/collegemanage/content{id}_11.shtml'.format(id = i)
            yield SplashRequest(url=_url, callback=self.parse_item,args={'wait': 3},meta={'id':i})

    def parse_item(self, response):
        try:
            title = response.xpath('//*[@id="gx211"]/div[4]/div[2]/ul[2]/li/h1/a/text()').extract()[0]
        except:
            with open('failed.txt','a+') as f:
                f.write(str(response.meta['id'])+',')
        items = response.xpath('//*[@class="trs"]')
        if items is not None:
            for i in items:
                item = gxzc()
                item['title'] = title
                item['content'] = ''
                item['catFirst'] = i.xpath('td[1]/a/text()').extract()[0]
                item['catSecond'] = i.xpath('td[2]/text()').extract()[0]
                item['catThird'] = i.xpath('td[3]/text()').extract()[0]
                item['url'] = response.url
                item['domain'] = 'www.gx211.com'
                yield item


