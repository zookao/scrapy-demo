import hashlib
import os
import sys
from typing import Any, Union, Tuple

import oss2
import pymysql
import requests


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


def getDatas():
    endpoint = "oss-cn-beijing.aliyuncs.com"
    access_key_id = ""
    access_key_secret = ""
    bucket_name = "libraryplus"
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    db = Database(host='mysql', port=3306, user='root', password='root', db='gerapy')
    sql = 'select * from chongqing where screenshot is null'
    results = db.select(sql)
    for item in results:
        url = item[1]
        url_hash = hashlib.md5(url.encode("utf8")).hexdigest()
        filename = f"{url_hash}.png"
        response = requests.get("http://192.168.56.102:8050/render.png?url=" + url + "&render_all=1&wait=0.5",
                                stream=True)
        with open(filename, "wb") as f:
            f.write(response.content)
        oss_result = bucket.put_object_from_file("cuqnews/file/" + filename, filename)
        if oss_result.status != 200:
            print(item[1] + "截图失败")
        else:
            sql = 'update chongqing set screenshot=%s where id=%s'
            update_result = db.update(sql,
                                      data=("https://img.libraryplus.bjadks.com/cuqnews/file/" + filename, item[0]))
            os.unlink(filename)
            print(item[1] + "截图成功")


if __name__ == '__main__':
    getDatas()
