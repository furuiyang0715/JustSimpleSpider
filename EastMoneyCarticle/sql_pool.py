import logging
import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

logger = logging.getLogger()


class PyMysqlPoolBase(object):
    """
        建立 mysql 连接池的 python 封装
        与直接建立 mysql 连接的不同之处在于连接在完成操作之后不会立即提交关闭
        可复用以提高效率
    """
    _pool = None

    def __init__(self,
                 host,
                 port,
                 user,
                 password,
                 db=None):
        self.db_host = host
        self.db_port = int(port)
        self.user = user
        self.password = str(password)
        self.db = db
        self.connection = self._getConn()
        self.cursor = self.connection.cursor()

    def _getConn(self):
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if PyMysqlPoolBase._pool is None:
            _pool = PooledDB(creator=pymysql,
                             mincached=1,
                             maxcached=20,
                             host=self.db_host,
                             port=self.db_port,
                             user=self.user,
                             passwd=self.password,
                             db=self.db,
                             use_unicode=True,
                             charset="utf8",
                             cursorclass=DictCursor)
        print("已经成功从连接池中获取连接")
        return _pool.connection()

    def _exec_sql(self, sql, param=None):
        if param is None:
            count = self.cursor.execute(sql)
        else:
            count = self.cursor.execute(sql, param)
        return count

    def insert(self, sql, params):
        """
        @summary: 更新数据表记录
        @param sql: SQL 格式及条件，使用 (%s,%s)
        @param params: 要更新的值: tuple/list
        @return: count 受影响的行数
        """
        return self._exec_sql(sql, params)

    def select_all(self, sql, params=None):
        self.cursor.execute(sql, params)
        results = self.cursor.fetchall()
        return results

    def select_many(self, sql, params=None, size=1):
        self.cursor.execute(sql, params)
        results = self.cursor.fetchmany(size)
        return results

    def select_one(self, sql, params=None):
        self.cursor.execute(sql, params)
        result = self.cursor.fetchone()
        return result

    def insert_many(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的 SQL 格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self.cursor.executemany(sql, values)
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: SQL 格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self._exec_sql(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: SQL 格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self._exec_sql(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self.connection.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self.connection.commit()
        else:
            self.connection.rollback()

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self.cursor.close()
        self.connection.close()


def mysql_test():
    import sys
    import time
    import pprint
    from GovSpiders.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

    conf = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "db_name": MYSQL_DB,
    }

    demo = PyMysqlPoolBase(**conf)
    print(demo)

    # (1) 测试创建连接
    print(demo.connection)

    # 测试数据库表信息
    table_name = "qq_Astock_news"
    comment = '腾讯财经[A股]'

    # (2) 测试建表语句
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
    drop_sql = f"""DROP TABLE IF EXISTS `{table_name}`; """
    # demo._exec_sql(drop_sql)

    # 测试插入一条数据
    insert_sql = f"""
    insert into `{table_name}` (`pub_date`, `title`, `link`, `article`) values (%s,%s,%s,%s);
    """
    values = ("2020-01-01", "我是标题", "我是链接"+str(time.time()), "我是正文")
    # demo.insert(insert_sql, values)

    # 测试查询全部数据
    sql = f"""select * from {table_name}; """
    # ret = demo.select_all(sql)
    # print(pprint.pformat(ret))

    # 测试查询 n 条数据
    sql = f"""select * from {table_name};"""
    # ret = demo.select_many(sql, size=3)
    # print(pprint.pformat(ret))

    # 测试查询单条数据
    sql = f"""select * from {table_name};"""
    # ret = demo.select_one(sql)
    # print(ret)

    # 测试插入多条数据
    datas = [
        ("2020-02-01", "我是标题", "我是链接"+str(time.time()),  "我是正文"),
        ("2020-02-01", "我是标题", "我是链接"+str(time.time()),  "我是正文"),
        ("2020-02-01", "我是标题", "我是链接"+str(time.time()),  "我是正文"),
        ("2020-02-01", "我是标题", "我是链接"+str(time.time()),  "我是正文"),
    ]
    # print(datas)
    insert_sql = f"""
    insert into `{table_name}` (`pub_date`, `title`, `link`, `article`) values (%s,%s,%s,%s);
    """
    # ret = demo.insert_many(insert_sql, datas)
    # print(ret)

    # 测试更新数据
    update_sql = f"update {table_name} set pub_date=%s where pub_date=%s; "
    data = [("2020-06-06"), ("2020-02-01")]
    # ret = demo.update(update_sql, data)
    # print(ret)

    # 测试删除数据
    sql7 = f"delete from {table_name} where id=%s "
    param7 = ["89"]
    # result7 = demo.delete(sql7, param7)
    # print(result7)

    # 最后要释放资源释放资源
    demo.dispose()


if __name__ == '__main__':
    mysql_test()
