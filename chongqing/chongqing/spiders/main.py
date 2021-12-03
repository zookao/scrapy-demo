import redis
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders.crawl import Rule
from scrapy_redis.spiders import RedisCrawlSpider

from chongqing.items import ChongqingItem
from chongqing.settings import *


class main(RedisCrawlSpider):

    # 入redis开始地址，如果有main:*，则跳过，根据学院调整代码
    def __init__(self, *a, **kw):
        redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0)
        check = False
        for key in redis_client.scan_iter('main:*', 1):
            check = True
            break
        if not check:
            redis_client.lpush('main:start_urls', 'http://news.cqu.edu.cn')
        super().__init__(*a, **kw)

    name = 'main'

    # 允许的域名，根据学院调整代码
    allow_domains = ['news.cqu.edu.cn']

    redis_key = 'main:start_urls'

    # 根据学院调整代码
    rules = (
        Rule(LinkExtractor(allow=(),deny=[r'.*(jpg|gif|png|doc|docx|xls|xlsx|pdf|rar|zip|ppt|pptx)$',r'.*DownloadAttachUrl.*'],allow_domains = allow_domains), follow=True, callback='parse_item'),
    )

    def parse_item(self, response):
        url = response.request.url
        title = response.xpath("//title[1]/text()").extract_first()
        keywords = response.xpath("//meta[@name='keywords'][1]/@content").extract_first()
        description = response.xpath("//meta[@name='description'][1]/@content").extract_first()
        content = response.xpath("//html[1]").extract_first()
        date = response.xpath("//div[@class='ibox']/span[2]/text()").extract_first()
        images = response.xpath("//img/@src").extract()
        files = response.xpath("//a[contains(@href,'.doc') or contains(@href,'.docx') or contains(@href,'.xls') or contains(@href,'.xlsx') or contains(@href,'.pdf') or contains(@href,'.rar') or contains(@href,'.zip') or contains(@href,'.ppt') or contains(@href,'.pptx') or contains(@href,'DownloadAttachUrl')]/@href").extract()
        item = ChongqingItem()
        item['url'] = url
        item['title'] = title
        item['keywords'] = keywords
        item['description'] = description
        item['content'] = content
        item['date'] = date
        item['images'] = images
        item['files'] = files
        yield item
