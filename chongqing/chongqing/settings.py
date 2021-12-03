# -*- coding: utf-8 -*-
BOT_NAME = 'chongqing'

SPIDER_MODULES = ['chongqing.spiders']
NEWSPIDER_MODULE = 'chongqing.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

COOKIES_ENABLED = False

SPIDER_MIDDLEWARES = {
    'chongqing.middlewares.ChongqingSpiderMiddleware': 543,
}

DOWNLOADER_MIDDLEWARES = {
    'chongqing.middlewares.RandomUserAgentMiddlware': 1,
    # 'chongqing.middlewares.RandomProxyMiddleware': 400,
    'chongqing.middlewares.ChongqingDownloaderMiddleware': 543,
}

ITEM_PIPELINES = {
    'chongqing.pipelines.DownloadImagePipeline': 301,
    'chongqing.pipelines.DownloadFilePipeline': 302,
    'chongqing.pipelines.ScreenshotPipeline': 300,
    'chongqing.pipelines.MysqlPipeline': 303,
}

HTTPERROR_ALLOWED_CODES = [403]

DOWNLOAD_DELAY = 3 #下载器在下载同一个网站下一个页面前需要等待的时间
CONCURRENT_REQUESTS_PER_IP = 1 #对单个IP进行并发请求的最大值
AUTOTHROTTLE_ENABLED = True # 0.5*DOWNLOAD_DELAY~1.5*DOWNLOAD_DELAY
AUTOTHROTTLE_START_DELAY = 1.0 #初始下载延迟
AUTOTHROTTLE_MAX_DELAY = 60.0 #在高延迟的情况下设置的最大下载延迟
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0 #Scrapy请求的平均数量应该并行发送每个远程服务器
AUTOTHROTTLE_DEBUG = True #启用显示所收到的每个响应的调节统计信息

MYSQL_HOST = "mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_PORT = 3306
MYSQL_DB = "gerapy"
MYSQL_TABLE = "chongqing"

REDIS_HOST = "redis"
REDIS_PARAMS = {"password": "111111"}
REDIS_PORT = 6379
REDIS_PASSWORD = 111111

OSS_ENDPOINT = "oss-cn-beijing.aliyuncs.com"
OSS_ACCESS_KEY = "" #指定oss的key
OSS_ACCESS_SECRET = ""
OSS_BUCKET = "libraryplus"

SPLASH_URL = "http://192.168.56.102:8050/"

OSS_URL_PREFIX = "https://img.libraryplus.bjadks.com/cuqnews/file/"

# 调度器启用Redis存储Requests队列
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 确保所有的爬虫实例使用Redis进行重复过滤
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 将Requests队列持久化到Redis，可支持暂停或重启爬虫
SCHEDULER_PERSIST = True

# Requests的调度策略，默认优先级队列
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'

# 将爬取到的items保存到Redis 以便进行后续处理
# ITEM_PIPELINES = {
#     'scrapy_redis.pipelines.RedisPipeline': 300
# }
