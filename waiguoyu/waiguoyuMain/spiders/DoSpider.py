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

    #http://www.cfl.cqu.edu.cn/
    #http://www.cfl.cqu.edu.cn/info/1180/9677.htm
    redis_key = 'waiguoyu:start_urls'

    rules = (
        Rule(LinkExtractor(allow=['\\w+/\\w+/\.htm']), follow=True),
        Rule(LinkExtractor(allow=['info/\\d+/\\d+\.htm']), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        url = response.request.url
        title = response.xpath("//div[@class='gl-cont-cont']/h1[1]/text()").extract()
        content = response.xpath("//div[@class='v_news_content'][1]").extract()
        time = response.xpath("//div[@class='gl-zz']/span[2]/span[2]/i[1]/text()").extract()
        images = response.xpath("//div[@class='v_news_content'][1]//img/src").extract()
        item = WaiguoyuMainItem()
        item['url'] = url
        item['title'] = title
        item['content'] = content
        item['time'] = time
        item['images'] = images
        yield item
