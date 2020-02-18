import logging
import re
import traceback

import pymysql
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

logger = logging.getLogger()


class MqlPipeline(object):

    def __init__(self, mysql_pool, db, table):
        self.mysql_pool = mysql_pool
        self.db = db
        self.table = table

    def contract_sql(self, to_insert):
        # 拼接需要执行的 mysql 语句
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}`.`{}` '''.format(self.db,
                                                       self.table) + fields_str + ''' values ''' + values_str + ''';'''
        return base_sql, tuple(vs)

    def _filter_char(self, test_str):
        # 处理特殊的空白字符
        # '\u200b' 是 \xe2\x80\x8b
        for cha in ['\n', '\r', '\t',
                    '\u200a', '\u200b', '\u200c', '\u200d', '\u200e',
                    '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
                    ]:
            test_str = test_str.replace(cha, '')
        test_str = test_str.replace(u'\xa0', u' ')  # 把 \xa0 替换成普通的空格
        return test_str

    def _process_content(self, vs):
        # 去除 4 字节的 utf-8 字符，否则插入mysql时会出错
        try:
            # python UCS-4 build的处理方式
            highpoints = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            # python UCS-2 build的处理方式
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

        params = list()
        for v in vs:
            # 对插入数据进行一些处理
            nv = highpoints.sub(u'', v)
            nv = self._filter_char(nv)
            params.append(nv)
        return params

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

    def update_datas(self, items):
        """
        更新数据
        :param items: [{"link": ... , "article": ... }, {} ...]
        :return:
        """
        _sql = f"update {self.db}.{self.table} set article=%s where link=%s"
        for item in items:
            try:
                param = [self.transferContent(item['article']), item['link']]
                self.mysql_pool.update(_sql, param)
            except:
                logger.warning("更新数据失败")
                self.mysql_pool._conn.rollback()
                traceback.print_exc()

        # 仅在清洗时使用 使用后立即销毁
        self.mysql_pool.dispose()

    def save_to_database(self, to_insert: dict):
        sql_w, vs = self.contract_sql(to_insert)
        # 预处理
        vs = [self.transferContent(v) for v in vs]
        # vs = [self._process_content(v) for v in vs]

        try:
            self.mysql_pool.insert(sql_w, vs)
            # print("正在插入 {} 到 mysql 数据库 ".format(vs))
            logger.info("正在插入 {} 到 mysql 数据库 ".format(vs))
            self.mysql_pool._conn.commit()
        except pymysql.err.IntegrityError:
            logger.warning("重复", to_insert)
            self.mysql_pool._conn.rollback()
        except Exception:
            logger.warning("mysql 插入出错, 请检查\n {}".format(to_insert))
            logger.warning("{}".format(sql_w))
            logger.warning("{}".format(vs))
            self.mysql_pool._conn.rollback()
            traceback.print_exc()


class BasePymysqlPool(object):
    def __init__(self, host, port, user, password, db_name=None):
        self.db_host = host
        self.db_port = int(port)
        self.user = user
        self.password = str(password)
        self.db = db_name
        self.conn = None
        self.cursor = None


class MyPymysqlPool(BasePymysqlPool):
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = Mysql.getConn()
            释放连接对象;conn.close()或del conn
    """
    # 连接池对象
    __pool = None

    def __init__(self, conf: dict):
        super(MyPymysqlPool, self).__init__(**conf)
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self._conn = self.__getConn()
        self._cursor = self._conn.cursor()

    def __getConn(self):
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if MyPymysqlPool.__pool is None:
            __pool = PooledDB(creator=pymysql,
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
        return __pool.connection()

    def getAll(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = []
        return result

    def getOne(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = None
        return result

    def getMany(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = []
        return result

    def insertMany(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql, values)
        return count

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def insert(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._conn.close()


# 测试数据库连接工具的使用


def mysql_test():
    # 创建连接对象
    from temp.chinabank.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD
    mysql = MyPymysqlPool({
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
        })

    # # 获取全部数据
    # sqlAll = "select * from test_furuiyang.chinabank_shujujiedu"
    # result = mysql.getAll(sqlAll)
    # # print(pprint.pformat(result))
    # print(len(result))

    # # 根据参数查询出其中的某条数据
    # sql2 = "select * from test_furuiyang.chinabank_shujujiedu where id=%s"
    # param2 = ["39"]
    # result = mysql.getOne(sql2, param2)
    # print(pprint.pformat(result))

    # # 根据输入参数查询出其中的某几条数据
    # param3 = []
    # param3.append(89)
    # param3.append(39)
    # sql3 = "select * from test_furuiyang.chinabank_shujujiedu where id in (%s,%s)"
    # result2 = mysql.getMany(sql3, 2, param3)
    # print(pprint.pformat(result2))

    # # 根据输入参数插入多个数据
    # sql4 = "insert into data_spider.testscore(q_a, q_b, score) values (%s,%s,%s)"
    # values4 = [(22, 33, 0.336222), (22, 33, 0.336222), (22, 33, 0.336222)]
    # result4 = mysql.insertMany(sql4, values4)
    # print(result4)

    # # 根据输入更新数据
    # sql5 = "update data_spider.testscore set score=%s where id=%s"
    # param5 = ["0.22222222", "6"]
    # result5 = mysql.update(sql5, param5)
    # print(result5)

    # # 根据输入参数插入数据
    # sql6 = "insert into data_spider.testscore(q_a, q_b, score) values (%s,%s,%s)"
    # param6 = ['55', '77', '0.225566']
    # result6 = mysql.insert(sql6, param6)
    # print(result6)

    # # 删除数据
    # sql7 = "delete from data_spider.testscore where id=%s "
    # param7 = ["5"]
    # result7 = mysql.delete(sql7, param7)
    # print(result7)

    # 最后要释放资源释放资源
    mysql.dispose()


if __name__ == '__main__':
    mysql_test()
