import logging

import pymysql

logger = logging.getLogger()


class PyMysqBase(object):
    """建立单个 mysql 数据库连接的 python 封装"""
    def __init__(self,
                 host='localhost',
                 port=3306,
                 user='user',
                 password='pwd',
                 db='db',
                 charset='utf8mb4',
                 cursorclass=pymysql.cursors.DictCursor,
                 ):
        self.connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            charset=charset,
            cursorclass=cursorclass
        )
        print("已经成功建立数据库连接")

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

    def __del__(self):
        print("数据库连接已经关闭")
        self.connection.close()


if __name__ == "__main__":
    import sys
    import time
    import pprint
    from GovSpiders.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
    conf = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "db": MYSQL_DB,
    }

    demo = PyMysqBase(**conf)

    # (1) 测试创建连接
    # print(demo.connection)

    # 测试数据库表信息
    table_name = "qq_Astock_news"
    comment = '腾讯财经[A股]'

    # (2) 测试建表语言
    create_sql = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
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
        ) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COMMENT='{comment}';
        """
    # demo._exec_sql(create_sql)

    # (3) 测试删除数据库
    # drop_sql = f"""DROP TABLE IF EXISTS `{table_name}`; """
    # demo._exec_sql(drop_sql)

    # 测试插入一条数据
    # insert_sql = f"""
    # insert into `{table_name}` (`pub_date`, `title`, `link`, `article`) values (%s,%s,%s,%s);
    # """
    # values = ("2020-01-01", "我是标题", "我是链接"+str(time.time()), "我是正文")
    # demo.insert(insert_sql, values)

    # 测试查询全部数据
    # sql = f"""select * from {table_name}; """
    # ret = demo.select_all(sql)
    # print(pprint.pformat(ret))

    # 测试查询 n 条数据
    # sql = f"""select * from {table_name};"""
    # ret = demo.select_many(sql, size=3)
    # print(pprint.pformat(ret))

    # 测试查询单条数据
    # sql = f"""select * from {table_name};"""
    # ret = demo.select_one(sql)
    # print(ret)

