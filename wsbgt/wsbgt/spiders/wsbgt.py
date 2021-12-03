# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from gerapy.spiders import CrawlSpider
from gerapy.spiders import Rule
from scrapy.loader import ItemLoader
from ..items import *
from scrapy.loader.processors import *


from scrapy import Request


class WsbgtSpider(CrawlSpider):
    def start_requests(self):
        yield Request(url=self.start_urls[0], dont_filter=True)
    
    def parse_page(self,response):
        catFirst = response.xpath('//*[@id="wrapper"]/div/div[1]/h3/text()').extract()[0]
        catSecond = response.xpath('//*[@id="wrapper"]/div/div[1]/div[1]/dl[1]/dd/a[@class="current"]/text()').extract()[0]
        catThird = response.xpath('//*[@id="wrapper"]/div/div[1]/div[1]/dl[2]/dd/a[@class="current"]/text()').extract()[0]
        year = response.xpath('//*[@id="wrapper"]/div/div[1]/div[1]/dl[3]/dd/a[@class="current"]/text()').extract()[0]
        hrefs = response.xpath('//*[@id="wrapper"]/div/div[2]/div[1]/div/dl/dt/a/@href')
        if hrefs is not None:
            for href in hrefs:
                yield Request(url=self.custom_settings['baseUrl']+href.extract(),meta={'catFirst':catFirst,'catSecond':catSecond,'catThird':catThird,'year':year},callback=self.parse_course, dont_filter=False,priority=10)
    
    def parse_course(self,response):
        courseName = response.xpath('//*[@id="wrapper"]/div/div[1]/div/div[2]/div[2]/div[1]/h3/text()').extract()[0]
        url = response.url
        ids = response.xpath('//*[@id="anthologyVideo"]/li/@id')
        if ids is not None:
            for id in ids:
                yield Request(url=url+'&videoId='+id.extract(),meta={'catFirst':response.meta['catFirst'],'catSecond':response.meta['catSecond'],'catThird':response.meta['catThird'],'year':response.meta['year'],'courseName':courseName},callback=self.parse_item, dont_filter=False,priority=11)

    name = 'wsbgt'
    allowed_domains = ['wsbgt.bjadks.com',]
    custom_settings = {
        "MYSQL_HOST": "mysql",
        "MYSQL_PORT": 3306,
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "root",
        "MYSQL_DATABASE": "gerapy",
        
        "baseUrl": "http://wsbgt.bjadks.com",
        "DOWNLOADER_MIDDLEWARES": {"gerapy.downloadermiddlewares.pyppeteer.PyppeteerMiddleware": 601, "scrapy_splash.SplashCookiesMiddleware": 723, "scrapy_splash.SplashMiddleware": 725, "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810},
        "SPIDER_MIDDLEWARES": {"scrapy_splash.SplashDeduplicateArgsMiddleware": 100},
        "ITEM_PIPELINES": {"gerapy.pipelines.MySQLPipeline": 300},
        }
    start_urls = ['http://wsbgt.bjadks.com/Course?firstcId=16&secondcId=92&thirdcId=0&year=2018&cataType=xsbg&orderByType=1&pageLayout=1&PageIndex=1&pageSize=10',]
    rules = (
         Rule(
            LinkExtractor(allow=['Course\\?firstcId=3&secondcId=[1-9]\\d*&thirdcId=0&year=\\d{4}&cataType=\\w{4}&orderByType=1&pageLayout=1&PageIndex=\\d+&pageSize=\\d+'], ),
            callback='parse_page', ),
         Rule(
            LinkExtractor(allow=['Course\\?firstcId=3&[^>"\']*'], ),
            follow=True, ),
        )
    
    
    def parse_item(self, response):
        loader = ItemLoader(item=wsbgt(), response=response)
        loader.add_value('courseName', response.meta['courseName'], )
        loader.add_xpath('title', '//*[@id="anthologyVideo"]/li[@class="current"]/a/text()')
        loader.add_xpath('content', '//*[@id="wrapper"]/div/div[1]/div/div[2]/div[2]/div[2]/h3/text()')
        loader.add_value('url', response.url, )
        loader.add_value('domain', "wsbgt.bjadks.com", )
        loader.add_value('catFirst', response.meta['catFirst'], )
        loader.add_value('catSecond', response.meta['catSecond'], )
        loader.add_value('catThird', response.meta['catThird'], )
        loader.add_value('year', response.meta['year'], )
        yield loader.load_item()
    
    