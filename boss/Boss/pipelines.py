# -*- coding: utf-8 -*-

import pymysql
from Boss.settings import mysql_table,mysql_db,mysql_host,mysql_port,mysql_user,mysql_password
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class BossPipeline(object):

    def __init__(self):
        self.db = pymysql.connect(mysql_host, mysql_user, mysql_password, mysql_db, charset='utf8',port=mysql_port)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'insert into %s (%s) values (%s)' % (mysql_table, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()

        return item
