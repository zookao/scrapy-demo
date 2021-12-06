import hashlib
import sys
import os
from typing import Any, Union, Tuple
from urllib.parse import urlparse

import oss2
import pymysql
import requests
from fake_useragent import UserAgent
from lxml import etree

import logging


class Database(object):
    def __init__(self, host, user, password, db, port=3306, charset="utf8"):
        try:
            self.connect = pymysql.connect(host=host, port=port, user=user,
                                           passwd=password,
                                           db=db, charset=charset, autocommit=True,
                                           cursorclass=pymysql.cursors.SSCursor)
            self.cursor = self.connect.cursor()
            logging.error("初始化")
        except pymysql.err as res:
            logging.error("链接出错了", str(res))

    def insert_all(self, insert_sql: str, data: dict) -> int:
        try:
            self.cursor.executemany(insert_sql, data)
            count = self.cursor.rowcount
            self.connect.commit()
            return count
        except Exception as e:
            self.connect.rollback()
            logging.error("添加多条数据出错:{}".format(e))

    def insert(self, insert_sql: str, data: tuple) -> int:
        try:
            self.cursor.execute(insert_sql, data)
            insert_id = self.connect.insert_id()
            self.connect.commit()
            return insert_id
        except Exception as e:
            self.connect.rollback()
            logging.error("添加单条数据出错:{}".format(e))

    def select(self, select_sql: str, data=None) -> tuple:
        try:
            self.cursor.execute(select_sql, data)
            result_all: Union[Tuple, Any] = self.cursor.fetchall()
            return result_all
        except Exception as e:
            self.connect.rollback()
            logging.error("查询数据出错:{}".format(e))

    def delete(self, delete_sql: str, data) -> int:
        try:
            self.cursor.execute(delete_sql, data)
            # 删除的影响行数
            row_count = self.cursor.rowcount
            # 提交事务
            self.connect.connect()
            return row_count
        except Exception as e:
            self.connect.rollback()
            logging.error("删除数据出错:{}".format(e))

    def update(self, update_sql, data):
        try:
            self.cursor.execute(update_sql, data)
            # 更新的影响行数
            row_count = self.cursor.rowcount
            # 提交事务
            self.connect.connect()
            return row_count
        except Exception as e:
            self.connect.rollback()
            logging.error("更新数据出错:{}".format(e))

    def __del__(self):
        self.connect.close()
        self.cursor.close()
        logging.error("关闭数据库")


def repair():
    endpoint = "oss-cn-beijing.aliyuncs.com"
    access_key_id = ""
    access_key_secret = ""
    bucket_name = "libraryplus"
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    db = Database(host='mysql', port=3306, user='root', password='root', db='gerapy')
    sql = 'select * from chongqing WHERE DATE>%s'
    results = db.select(sql, data=('2020-11-20'))
    ua = UserAgent(path="/usr/src/app/fake_useragent_0.1.11.json")
    for data in results:
        logging.error('=======id：' + str(data[0]))
        url = data[1]
        schema = urlparse(url).scheme
        domain = urlparse(url).netloc
        base = schema + '://' + domain + '/'
        response = requests.get(url, headers={'User-Agent': ua.random})
        html = etree.HTML(response.content)
        items = html.xpath('//img/@src')
        for item in items:
            if len(item) != 0:
                if '/' in item:
                    image_name = item.split('/')[-1]
                else:
                    image_name = item

                oss_url = "https://img.libraryplus.bjadks.com/cuqnews/file/" + image_name
                logging.error('oss地址：' + oss_url)

                if 'http' in item:
                    real_url = item.replace('mp.cqu.edu.cn','news.cqu.edu.cn')
                else:
                    if '../' in item:
                        real_url = base + item.replace('../', '')
                    else:
                        real_url = base + item

                exist = bucket.object_exists("cuqnews/file/" + image_name)
                if exist:
                    meta_data = bucket.get_object_meta("cuqnews/file/" + image_name)
                    size = meta_data.content_length
                    if size < 1000:
                        logging.error(image_name + '文件过小，重新下载并上传')
                        logging.error('下载地址：' + real_url)
                        try:
                            response = requests.get(real_url, headers={'User-Agent': ua.random}, timeout=3)
                            result = bucket.put_object("cuqnews/file/" + image_name, response)
                            if result.status != 200:
                                logging.error(item + '上传图片失败')
                                continue
                            logging.error(item + '上传图片成功')
                        except:
                            continue
                else:
                    logging.error(image_name + '文件不存在，开始下载并上传')
                    logging.error('下载地址：' + real_url)
                    try:
                        response = requests.get(real_url, headers={'User-Agent': ua.random}, timeout=3)
                        result = bucket.put_object("cuqnews/file/" + image_name, response)
                        if result.status != 200:
                            logging.error(item + '上传图片失败')
                            continue
                        logging.error(item + '上传图片成功')
                    except:
                        continue


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR,  # 控制台打印的日志级别
                        filename='log.log',
                        filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                        # a是追加模式，默认如果不写的话，就是追加模式
                        format=
                        '%(asctime)s - %(message)s'  # 日志格式
                        )
    repair()
