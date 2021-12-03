import redis
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders.crawl import Rule
from scrapy_redis.spiders import RedisCrawlSpider

from waiguoyuMain.items import WaiguoyuMainItem
from waiguoyuMain.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


class WaiguoyuMainSpider(RedisCrawlSpider):
    # redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT,password=REDIS_PASSWORD,db=0)

    name = "WaiguoyuMainSpider"
    # 允许的域名
    allow_domains = ["cqu.edu.cn"]
    redis_key = 'waiguoyu:start_urls'  # http://www.cfl.cqu.edu.cn/

    rules = (
        Rule(LinkExtractor(allow=['\\w+/\\w+/\.htm']), follow=True),
        Rule(LinkExtractor(allow=['info/\\d+/\\d+\.htm']),callback='parse_item',follow=True),
    )

    def parse_item(self, response):
        title = response.xpath("//div[@class='article']/h1/text()").extract_first()
        temp = response.xpath("//div[@class='topic-content']//text()").extract()
        content = ' '.join(temp)
        url = response.request.url
        item = WaiguoyuMainItem()
        item['title'] = title
        item['content'] = content
        item['url'] = url
        yield item
