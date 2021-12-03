# -*- coding: utf-8 -*-
from scrapy_redis.spiders import RedisSpider
from scrapy.loader import ItemLoader
from ..items import *
from scrapy.loader.processors import *


from scrapy import Request
from scrapy import FormRequest
import re


class SybkSpider(RedisSpider):
    name = 'sybk'
    allowed_domains = ['baike.shangyekj.com',]
    custom_settings = {
        "MYSQL_HOST": "mysql",
        "MYSQL_PORT": 3306,
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "root",
        "MYSQL_DATABASE": "gerapy",

        "DOWNLOADER_MIDDLEWARES": {'sybk.middlewares.RandomUserAgentMiddlware': 333,"gerapy.downloadermiddlewares.pyppeteer.PyppeteerMiddleware": 601, "scrapy_splash.SplashCookiesMiddleware": 723, "scrapy_splash.SplashMiddleware": 725, "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810},

        "SPIDER_MIDDLEWARES": {"scrapy_splash.SplashDeduplicateArgsMiddleware": 100},

        "ITEM_PIPELINES": {"gerapy.pipelines.MySQLPipeline": 300},

        "REDIS_HOST": "redis",
        "REDIS_PARAMS": {"password": "caozongchao", },
        "REDIS_PORT": 6379,

        "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
        "SCHEDULER_QUEUE_CLASS": "scrapy_redis.queue.SpiderPriorityQueue",
        "DUPEFILTER_CLASS": "scrapy_redis.dupefilter.RFPDupeFilter",
        "SCHEDULER_PERSIST": True,

        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        }
    }
    redis_key = 'sybk:start_urls' #http://baike.shangyekj.com/list.aspx
    baseUrl = 'http://baike.shangyekj.com/'
    apiUrl = 'http://baike.shangyekj.com/AlbumUI.axd'

    def parse(self,response):
        data = {'action':'GetCatalogByBaiKe','top':'0','showOrder':'','pid':'14'}
        yield FormRequest(url=self.apiUrl,formdata=data,callback=self.parse_first_category)

    def parse_first_category(self,response):
        items = response.xpath('/Template/Item')
        if items is not None:
            for item in items:
                catFirstId = item.xpath('Id/text()').extract()[0]
                catFirstName = item.xpath('Name/text()').extract()[0]
                data = {'action':'GetCatalogByChilds','id':catFirstId,'showOrder':'3'}
                yield FormRequest(url=self.apiUrl,formdata=data,callback=self.parse_second_category,meta={'catFirst':catFirstName},priority=10)

    def parse_second_category(self,response):
        items = response.xpath('/Template/Item')
        if items is not None:
            for item in items:
                catFirstName = response.meta['catFirst']
                catSecondName = item.xpath('Name/text()').extract()[0]
                # 三级分类
                its = item.xpath('Child/Item')
                if  its is not None:
                    for it in its:
                        catThirdId = it.xpath('Id/text()').extract()[0]
                        catThirdName = it.xpath('Name/text()').extract()[0]
                        data = {'action':'GetAlbumByCatalogPage','showOrder':'3','page':'1','pageSize':'20','catalogid':catThirdId,'dateCond':'','htmlFile':'/WebUI/XML/list_3.xml'}
                        yield FormRequest(url=self.apiUrl,formdata=data,callback=self.parse_page,meta={'catFirst':catFirstName,'catSecond':catSecondName,'catThird':catThirdName,'catalogid':catThirdId},priority=20)

    def parse_page(self,response):
        catFirst = response.meta['catFirst']
        catSecond = response.meta['catSecond']
        catThird = response.meta['catThird']
        catalogid = response.meta['catalogid']
        content = response.xpath('/Template/Content/text()').extract()[0]
        linkIds = re.findall(r"<h3><a href=\"detail.aspx\?id=(\d+)\"" ,content)
        if linkIds is not None:
            for linkId in linkIds:
                data = {'action':'GetAlbumInfo','id':linkId}
                yield FormRequest(url=self.apiUrl,formdata=data,callback=self.parse_video,meta={'catFirst':catFirst,'catSecond':catSecond,'catThird':catThird,'videoId':linkId},priority=30)

        pages = response.xpath('/Template/TotalPage/text()').extract()[0]
        for i in range(2,int(pages) + 1):
            data = {'action':'GetAlbumByCatalogPage','showOrder':'3','page':str(i),'pageSize':'20','catalogid':catalogid,'dateCond':'','htmlFile':'/WebUI/XML/list_3.xml'}
            yield FormRequest(url=self.apiUrl,formdata=data,callback=self.parse_page,meta={'catFirst':catFirst,'catSecond':catSecond,'catThird':catThird,'catalogid':catalogid},priority=20)

    def parse_video(self,response):
        courseName = response.xpath('/Template/Item/C_Title/text()').extract()[0]
        title = response.xpath('/Template/Item/Files/Item/C_Name/text()').extract()[0]
        content = response.xpath('/Template/Item/C_Description/text()').extract()[0]
        loader = ItemLoader(item=sybk(), response=response)
        loader.add_value('courseName', courseName)
        loader.add_value('title', title)
        loader.add_value('content', content)
        loader.add_value('url', self.baseUrl+'detail.aspx?id='+response.meta['videoId'], )
        loader.add_value('domain', "baike.shangyekj.com", )
        loader.add_value('catFirst', response.meta['catFirst'], )
        loader.add_value('catSecond', response.meta['catSecond'], )
        loader.add_value('catThird', response.meta['catThird'], )
        yield loader.load_item()

