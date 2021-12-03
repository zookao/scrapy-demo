from .template_engine import generate_crawl

DB_HOST = 'mysql'
DB_PORT = '3306'
DB_USER = 'root'
DB_PASS = 'root'
DB_NAME = 'cs'

class Db(object):
    def __init__(self):
        self.dbconn = None
        self.dbcurr = None

    def check_conn(self):
        try:
            self.dbconn.ping()
        except:
            return False
        else:
            return True

    def conn(self):
        self.dbconn = pymysql.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME, charset='utf8')
        self.dbconn.autocommit(False)
        self.dbcurr = self.dbconn.cursor()

    def fetchone(self):
        return self.dbcurr.fetchone()

    def fetchall(self):
        return self.dbcurr.fetchall()

    def execute(self, sql, args=None, falg=False):
        if not self.dbconn:
            # 第一次链接数据库
            self.conn()
        try:
            if args:
                rs = self.dbcurr.execute(sql, args)
            else:
                rs = self.dbcurr.execute(sql)
            return rs
        except Exception as e:
            if self.check_conn():
                print('执行sql失败')
                traceback.print_exc()
            else:
                print('重连mysql')
                self.conn()
                if args:
                    rs = self.dbcurr.execute(sql, args)
                else:
                    rs = self.dbcurr.execute(sql)
                return rs

    def commit(self):
        self.dbconn.commit()

    def rollback(self):
        self.dbconn.rollback()

    def close(self):
        self.dbconn.close()
        self.dbcurr.close()

    def last_row_id(self):
        return self.dbcurr.lastrowid

db = DB()
rules = db.query(Rule).filter(Rule.enable == 1)
for rule in rules:
    generate_crawl(project, rule)