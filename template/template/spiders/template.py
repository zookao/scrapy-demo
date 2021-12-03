# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
from crawler.items import CsItem
from scrapy.spiders import Rule
import html2text

class CsSpider(RedisCrawlSpider):
    name = 'cs'
    allowed_domains = ['bjadks.com','wsbgt.com']
    redis_key = 'cs:start_urls'

    rules = (
        # follow all links
        Rule(LinkExtractor(), callback='parse_page', follow=True),
    )

    def __init__(self, *args, **kwargs):
        # 修改这里的类名为当前类名
        super(CsSpider, self).__init__(*args, **kwargs)

    def parse_page(self, response):
        item = CsItem()
        item['title'] = response.css('title::text').extract()[0]
        item['link'] = response.request.url
        body = response.xpath('/html/body').extract()[0]

        converter = html2text.HTML2Text()
        converter.ignore_links = True
        finalBody = converter.handle(body)
        item['body'] = finalBody

        yield item
