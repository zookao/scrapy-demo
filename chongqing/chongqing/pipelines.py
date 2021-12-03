# -*- coding: utf-8 -*-
import hashlib
import logging
import os
from urllib.parse import quote
from urllib.parse import urlparse

import oss2
import pymysql
import requests
import scrapy
from fake_useragent import UserAgent
from itemadapter import ItemAdapter

from chongqing.settings import *


class DownloadImagePipeline(object):

    def __init__(self):
        '''创建oss连接对象'''
        self.endpoint = OSS_ENDPOINT
        self.access_key_id = OSS_ACCESS_KEY
        self.access_key_secret = OSS_ACCESS_SECRET
        self.bucket_name = OSS_BUCKET
        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
        self.ua = UserAgent(use_cache_server=False)

    def process_item(self, item, spider):
        schema = urlparse(item['url']).scheme
        domain = urlparse(item['url']).netloc
        base = schema + '://' + domain + '/'
        print('域名：'+base)
        for image_url in item['images']:
            if len(image_url) != 0:
                if '/' in image_url:
                    image_name = image_url.split('/')[-1]
                else:
                    image_name = image_url

                ossUrl = OSS_URL_PREFIX + image_name
                print('ossUrl：'+ossUrl)

                if 'http' in image_url:
                    real_url = image_url
                else:
                    if '../' in image_url:
                        real_url = base + image_url.replace('../', '')
                    else:
                        real_url = base + image_url
                print('real_url：'+real_url)
                try:
                    response = requests.get(real_url,headers={'User-Agent': self.ua.random})
                    result = self.bucket.put_object("cuqnews/file/" + image_name, response)
                    if result.status != 200:
                        logging.info(image_url + '上传图片失败')
                        continue
                    logging.info(image_url + '上传图片成功')
                    item['content'] = item['content'].replace(image_url, ossUrl)
                    logging.info(image_url + '替换图片成功')
                except:
                    continue
        return item


class DownloadFilePipeline(object):

    def process_item(self, item, spider):
        schema = urlparse(item['url']).scheme
        domain = urlparse(item['url']).netloc
        base = schema + '://' + domain + '/'
        for file_url in item['files']:
            if len(file_url) != 0:
                if 'http' in file_url:
                    real_url = file_url
                else:
                    if '../' in file_url:
                        file_url = base + file_url.replace('../', '')
                    else:
                        real_url = base + file_url
                try:
                    item['content'] = item['content'].replace(file_url, real_url)
                    logging.info(file_url + '替换附件成功')
                except:
                    continue
        return item


class ScreenshotPipeline:
    SPLASH_URL = SPLASH_URL + "render.png?url={}&render_all=1&wait=0.5"

    def __init__(self):
        '''创建oss连接对象'''
        self.endpoint = OSS_ENDPOINT
        self.access_key_id = OSS_ACCESS_KEY
        self.access_key_secret = OSS_ACCESS_SECRET
        self.bucket_name = OSS_BUCKET
        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)

    async def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        encoded_item_url = quote(adapter["url"])
        screenshot_url = self.SPLASH_URL.format(encoded_item_url)
        request = scrapy.Request(screenshot_url)
        response = await spider.crawler.engine.download(request, spider)

        if response.status != 200:
            return item

        url = adapter["url"]
        url_hash = hashlib.md5(url.encode("utf8")).hexdigest()
        filename = f"{url_hash}.png"
        with open(filename, "wb") as f:
            f.write(response.body)
        result = self.bucket.put_object_from_file("cuqnews/file/" + filename, filename)
        if result.status != 200:
            logging.info('上传截图失败')
        else:
            logging.info('上传截图成功')
            adapter["screenshot"] = OSS_URL_PREFIX + filename
        os.unlink(filename)
        return item


class MysqlPipeline(object):

    def __init__(self):
        self.db = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB,
                                  charset='utf8', port=MYSQL_PORT)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        del item['images']
        del item['files']
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'insert into %s (%s) values (%s)' % (MYSQL_TABLE, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()

        return item
