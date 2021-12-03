import hashlib
import sys
from typing import Any, Union, Tuple
from urllib.parse import urlparse

import oss2
import pymysql
import requests
from fake_useragent import UserAgent
from lxml import etree


class Database(object):
    def __init__(self, host, user, password, db, port=3306, charset="utf8"):
        try:
            self.connect = pymysql.connect(host=host, port=port, user=user,
                                           passwd=password,
                                           db=db, charset=charset, autocommit=True,cursorclass = pymysql.cursors.SSCursor)
            self.cursor = self.connect.cursor()
            print("初始化")
        except pymysql.err as res:
            print("链接出错了", str(res))

    def insert_all(self, insert_sql: str, data: dict) -> int:
        try:
            self.cursor.executemany(insert_sql, data)
            count = self.cursor.rowcount
            self.connect.commit()
            return count
        except Exception as e:
            self.connect.rollback()
            print("添加多条数据出错:{}".format(e))

    def insert(self, insert_sql: str, data: tuple) -> int:
        try:
            self.cursor.execute(insert_sql, data)
            insert_id = self.connect.insert_id()
            self.connect.commit()
            return insert_id
        except Exception as e:
            self.connect.rollback()
            print("添加单条数据出错:{}".format(e))

    def select(self, select_sql: str, data=None) -> tuple:
        try:
            self.cursor.execute(select_sql, data)
            result_all: Union[Tuple, Any] = self.cursor.fetchall()
            return result_all
        except Exception as e:
            self.connect.rollback()
            print("查询数据出错:{}".format(e))

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
            print("删除数据出错:{}".format(e))

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
            print("更新数据出错:{}".format(e))

    def __del__(self):
        self.connect.close()
        self.cursor.close()
        print("关闭数据库")

def repair():
    endpoint = "oss-cn-beijing.aliyuncs.com"
    access_key_id = ""
    access_key_secret = ""
    bucket_name = "libraryplus"
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    db = Database(host='mysql', port=3306, user='root', password='root', db='gerapy')
    sql = 'select * from chongqing WHERE DATE>%s and id>%s'
    results = db.select(sql,data=('2020-11-20',1))
    ua = UserAgent(use_cache_server=False)
    for data in results:
        url = data[1]
        response = requests.get(url,headers={'User-Agent': ua.random})
        html = etree.HTML(response.content)
        items = html.xpath('//img/@src')
        for item in items:
            schema = urlparse(item).scheme
            domain = urlparse(item).netloc
            base = schema + '://' + domain + '/'
            print('域名：'+base)
            if len(item) != 0:
                if '/' in item:
                    image_name = item.split('/')[-1]
                else:
                    image_name = item

                ossUrl = "https://img.libraryplus.bjadks.com/cuqnews/file/" + image_name
                print('ossUrl：'+ossUrl)

                if 'http' in item:
                    real_url = item
                else:
                    if '../' in item:
                        real_url = base + item.replace('../', '')
                    else:
                        real_url = base + item
                print('real_url：'+real_url)
                try:
                    response = requests.get(real_url,headers={'User-Agent': ua.random})
                    result = bucket.put_object("cuqnews/file/" + image_name, response)
                    if result.status != 200:
                        print(item + '上传图片失败')
                        continue
                    print(item + '上传图片成功')
                    item['content'] = item['content'].replace(item, ossUrl)
                    print(item + '替换图片成功')
                except:
                    continue

if __name__ == '__main__':
    repair()