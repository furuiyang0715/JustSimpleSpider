import datetime
import sys
import time

import pymysql

from money_163.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from money_163.my_log import logger


class PyMysqBase(object):
    def __init__(self,
                 host='localhost',
                 port=3306,
                 user='user',
                 password='pwd',
                 db='db',
                 charset='utf8mb4',
                 cursorclass=pymysql.cursors.DictCursor,
                 ):
        while True:
            try:
                self.connection = pymysql.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    db=db,
                    charset=charset,
                    cursorclass=cursorclass
                )
            except:
                logger.warning("无法建立更多连接, 请等一等哈..")
                time.sleep(3)
            else:
                # logger.debug("已经成功建立数据库连接")
                break

    def _exec_sql(self, sql):
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
        self.connection.commit()

    def insert(self, sql, params):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
        self.connection.commit()

    def select_all(self, sql, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            results = cursor.fetchall()
        return results

    def select_many(self, sql, params=None, size=1):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            results = cursor.fetchmany(size)
        return results

    def select_one(self, sql, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchone()
        return result

    def close(self):
        # logger.info("手动关闭连接")
        self.connection.close()

    def __del__(self):
        try:
            self.connection.close()
        except:
            pass


class StoreTool(PyMysqBase):
    def transferContent(self, content):
        if content is None:
            return None
        else:
            string = ""
            for c in content:
                if c == '"':
                    string += '\\\"'
                elif c == "'":
                    string += "\\\'"
                elif c == "\\":
                    string += "\\\\"
                else:
                    string += c
            return string

    def save(self, item: dict):
        logger.info("要保存的数据是{}".format(item))
        link = item.get("l")
        title = item.get("t")
        pub_date = item.get("p")
        article = item.get("article")

        insert_sql = """
        insert into `netease_money` (`pub_date`, `title`, `link`, `article`) values (%s,%s,%s,%s);
        """
        try:
            try:
                self.insert(insert_sql, (pub_date, title, link, article))
            except:
                article = self.transferContent(article)
                self.insert(insert_sql, (pub_date, title, link, article))
        except pymysql.err.IntegrityError:
            logger.warning("重复插入")
        else:
            logger.info("保存成功")

    def _is_exist(self, link):
        ret = self.select_one("select * from `netease_money` where link = %s;", (link))
        if ret:
            return True
        else:
            return False


if __name__ == "__main__":
    conf = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "db": MYSQL_DB,
    }

    # 建立连接
    demo = PyMysqBase(**conf)
    print(demo.connection)

    # 测试建表语言
    create_sql = """
    CREATE TABLE `netease_money` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `pub_date` datetime NOT NULL COMMENT '发布时间',
      `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
      `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
      `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
      `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
      `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      UNIQUE KEY `link` (`link`),
      KEY `pub_date` (`pub_date`)
    ) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COMMENT='网易财经';

    """
    # 建表
    # demo._exec_sql("DROP TABLE IF EXISTS `netease_money`;")
    # demo._exec_sql(create_sql)

    # 删表
    drop_sql = """drop table netease_money; """
    # demo._exec_sql(drop_sql)

    # 测试插入一条数据
    insert_sql = """
    insert into `netease_money` (`pub_date`, `title`, `link`, `article`) values (%s,%s,%s,%s);
    """
    values = ("2020-01-01", "我是标题", "我是链接3", "我是正文")
    # demo.insert(insert_sql, values)

    # 测试查询全部数据
    sql = """select * from netease_money; """
    # ret = demo.select_all(sql)
    # print(ret)

    # 测试查询两条数据
    sql = """select * from netease_money;"""
    # ret = demo.select_many(sql, size=3)
    # print(ret)

    # 测试查询单条数据
    sql = """select * from netease_money;"""
    # ret = demo.select_one(sql)
    # print(ret)