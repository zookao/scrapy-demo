# -*- coding: utf-8 -*-

import pymysql
from waiguoyuMain.settings import MYSQL_TABLE,MYSQL_DB,MYSQL_HOST,MYSQL_PORT,MYSQL_USER,MYSQL_PASSWORD
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class WaiguoyuMainPipeline(object):

    def __init__(self):
        self.db = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, db=MYSQL_DB, charset='utf8',port=MYSQL_PORT)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'insert into %s (%s) values (%s)' % (MYSQL_TABLE, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()

        return item
