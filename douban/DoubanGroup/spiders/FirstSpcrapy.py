import scrapy
from DoubanGroup.items import DoubanItem
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.spiders.crawl import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Request

class doubanSpider(RedisCrawlSpider):
    name = "doubanSpider"
    #允许的域名
    allow_domains = ["douban.com"]
    redis_key = 'douban:start_urls'

    rules = (
        Rule(LinkExtractor(allow=['/discussion\\?start=\\d+']), follow=True),
        Rule(LinkExtractor(allow=['/topic/\\d+/$']),callback='parse_item',follow=True),
    )

    def parse_item(self, response):
        title = response.xpath("//div[@class='article']/h1/text()").extract_first()
        temp = response.xpath("//div[@class='topic-content']//text()").extract()
        content = ' '.join(temp)
        url = response.request.url
        item = DoubanItem()
        item['title'] = title
        item['content'] = content
        item['url'] = url
        yield item
