# -*- coding: utf-8 -*-

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'


ROBOTSTXT_OBEY = False

SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER_PERSIST = True

FEED_EXPORT_ENCODING = 'utf-8'

ITEM_PIPELINES = {
    'crawler.pipelines.CrawlerPipeline': 300,
    'scrapy_redis.pipelines.RedisPipeline': 400,
}
REDIS_HOST = 'redis'
REDIS_PARAMS = {
    'password': 'caozongchao',
}
REDIS_PORT = 6379

DOWNLOADER_MIDDLEWARES = {
   'crawler.middlewares.RandomUserAgentMiddlware': 333,
}