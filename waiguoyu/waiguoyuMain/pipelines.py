# -*- coding: utf-8 -*-

import pymysql
from waiguoyuMain.settings import MYSQL_TABLE, MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD
import requests


class DownloadImagePipeline(object):

    def process_item(self, item, spider):
        base = 'http://www.cfl.cqu.edu.cn/'
        for image_url in item['images']:
            if '/' in image_url:
                image_name = image_url.split('/')[-1]
            else:
                image_name = image_url

            if 'http' in image_url:
                realUrl = image_url
            else:
                realUrl = base + image_url
            try:
                response = requests.get(realUrl, timeout=(4, 7))
                img = response.content
                with open(image_name, 'wb') as f:
                    f.write(img)
                item['content'].replace(image_url, image_name);
            except:
                continue
        return item


class WaiguoyuMainPipeline(object):

    def __init__(self):
        self.db = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB,charset='utf8', port=MYSQL_PORT)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        del item['images']
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'insert into %s (%s) values (%s)' % (MYSQL_TABLE, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()

        return item

# class DownloadImagePipeline(object):
#     '''上传图片到oss的管道'''
#
#     def __init__(self):
#         '''创建oss连接对象'''
#         self.endpoint = config.OSS_ENDPOINT
#         self.access_key_id = config.OSS_ACCESS_KEY_ID
#         self.access_key_secret = config.OSS_ACCESS_KEY_SECRET
#         self.bucket_name = config.OSS_IMG_BUCKET_NAME
#         self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
#         self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
#         self.rf = RequestFilter()
#
#     def process_item(self, item, spider):
#         item['image_paths'] = []
#         for image_url in item['image_urls']:
#             image_name = self.calSha1(image_url)
#             if self.rf.imgurl_is_exists(image_url):
#                 item['image_paths'].append("oss地址" + image_name)
#                 print('该图片链接已经请求过啦')
#
#             else:
#                 # 处理错误链接
#                 try:
#                     image_input = requests.get(image_url, timeout=(4, 7))
#                 except:
#                     item['image_paths'].append("")
#                     continue
#                 # 上传到oss
#                 result = self.bucket.put_object("image/" + image_name, image_input)
#                 if result.status == 200:
#                     # print("该图片上传成功")
#                     item['image_paths'].append("oss地址" + image_name)
#                     self.rf.mark_url(image_url)
#         return item
#
#     def calSha1(self, image_url):
#         '''给image_url加密'''
#         sha1obj = hashlib.sha1()
#         sha1obj.update(image_url.encode())
#         hash = sha1obj.hexdigest()
#         return hash + '.jpg'
