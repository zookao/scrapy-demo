# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.linkextractors import LinkExtractor
from gerapy.spiders import Rule
from ..items import *

from scrapy import Request
from scrapy_splash import SplashRequest

import re

class JdyxSpider(RedisCrawlSpider):
    name = 'jdyx'
    allowed_domains = ['jd.com','3.cn']
    custom_settings = {
        "MYSQL_HOST": "mysql",
        "MYSQL_PORT": 3306,
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "root",
        "MYSQL_DATABASE": "gerapy",

        "ROBOTSTXT_OBEY": False,
        # 最大抓取深度，以防无限递归
        "DEPTH_LIMIT": 100,
        #请求并发数
        "CONCURRENT_REQUESTS": 50,

        # 关闭scrapy 某些扩展，以提高抓取效率
        "RETRY_ENABLED": False,
        "TELNETCONSOLE_ENABLED": False,

        "DOWNLOADER_MIDDLEWARES": {
            'jdyx.middlewares.RandomUserAgentMiddlware': 333,
            # "scrapy_splash.SplashCookiesMiddleware": 723,
            # "scrapy_splash.SplashMiddleware": 725,
            # "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
            # "jdyx.middlewares.ProxyMiddleWare": 843,
        },

        "SPIDER_MIDDLEWARES": {
            # "scrapy_splash.SplashDeduplicateArgsMiddleware": 100
        },

        # "SPLASH_URL": 'http://splash:8050',

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
    }

    redis_key = 'jdyx:start_urls'

    rules = (
        Rule(
            LinkExtractor(
                allow=['list.html\?cat=[^"\']*'],
                restrict_xpaths=['//*[@id="p-category"]/div','//*[@id="J_main"]/div[1]/div/div[4]'],
            ),
            callback='parse_list',
            follow=True,
        ),
    )

    def parse_list(self, response):
        items = response.xpath('//*[@id="plist"]/ul/li')
        if items is not None:
            for item in items:
                href = item.xpath('div/div[1]/a/@href').extract_first()
                img = item.xpath('div/div[1]/a/img/@src').extract_first()
                _id = item.xpath('div/@data-sku').extract_first()
                if href is not None and img is not None and _id is not None:
                     yield Request(
                         url='https:'+href,
                         meta={'img':'https:'+img,'_id':_id},
                         callback=self.parse_item,
                         priority=10
                     )


    def parse_item(self, response):
        item = jdyx()
        cat = response.xpath('//*[@id="crumb-wrap"]/div/div[1]/div').extract()
        length = len(cat)
        item['catFirst'] = response.xpath('//*[@id="crumb-wrap"]/div/div[1]/div[1]/a/text()').extract_first()
        item['catSecond'] = response.xpath('//*[@id="crumb-wrap"]/div/div[1]/div[3]/a/text()').extract_first()
        item['catThird'] = response.xpath('//*[@id="crumb-wrap"]/div/div[1]/div[5]/a/text()').extract_first()
        if length == 9:
            item['catFourth'] = response.xpath('//*[@id="crumb-wrap"]/div/div[1]/div[7]/a/text()').extract_first()
        else:
            item['catFourth'] = ''

        if length == 9:
            item['title'] = response.xpath('//*[@id="crumb-wrap"]/div/div[1]/div[9]/text()').extract_first()
        else:
            item['title'] = response.xpath('//*[@id="crumb-wrap"]/div/div[1]/div[7]/text()').extract_first()

        desc_url = 'https://'+re.findall('desc: \'\/\/([^\']*)\'',response.text)[0]

        item['publishing_house'] = ''
        params = ''
        intro = response.xpath('//*[@id="parameter2"]/li')
        if intro is not None:
            for i in intro:
                s = i.xpath('.//text()').extract()[0]
                params = params+s+'<br />'
                if  '出版社：' in s:
                    item['publishing_house'] = s

        item['img'] = response.meta['img']

        price_url = 'http://pm.3.cn/prices/pcpmgets?callback=jQuery&skuids=%s' % response.meta['_id']

        item['url'] = response.url
        item['domain'] = 'jd.com'
        yield Request(
            url=price_url,
            meta={'item':item,'desc_url':desc_url,'params':params},
            callback=self.parse_price,
            priority=20
        )

    def parse_price(self,response):
        item = response.meta['item']
        desc_url = response.meta['desc_url']
        params = response.meta['params']
        price_text = response.text.strip()
        item['price'] = re.findall('([1-9]\d*\.?\d*)|(0\.\d*[1-9])',price_text)[-1][0]
        yield Request(
            url=desc_url,
            meta={'item':item,'desc_url':desc_url,'params':params},
            callback=self.parse_content,
            priority=30
        )

    def parse_content(self,response):
        item = response.meta['item']
        params = response.meta['params']
        content_text = response.text.strip()
        content = re.findall('"content":"(.*)"}',content_text)[0].strip()
        item['content'] = params+content
        yield item
        # print(item)