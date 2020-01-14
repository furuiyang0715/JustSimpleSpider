# -*- coding: utf-8 -*-

import logging
import os
import pprint
import re
import sys
import time
import traceback

import pymysql
import requests
import json
from lxml import html
from selenium import webdriver
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

logger = logging.getLogger()

env = os.environ

MYSQL_HOST = env.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = env.get("MYSQL_PORT", 3307)
MYSQL_USER = env.get("MYSQL_USER", "root")
MYSQL_PASSWORD = env.get("MYSQL_PASSWORD", "ruiyang")
MYSQL_DB = env.get("MYSQL_DB", "test_furuiyang")
MYSQL_TABLE = env.get("MYSQL_TABLE", "gov_stats_zxfb")
ALL_PAGES = int(env.get("ALL_PAGES", 25))
SELENIUM_HOST = env.get("SELENIUM_HOST", "172.17.0.6")


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
            print("重复", to_insert.get("link"))
            # logger.warning("重复{}".format(to_insert))
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


class GovStats(object):
    # 国家统计局爬虫
    def __init__(self):
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Referer': 'https://m.douban.com/movie/nowintheater?loc_id=108288',
        }
        # 国家统计局需要爬取的版块有: 
        # 最新发布 ... 
        if MYSQL_TABLE == "gov_stats_zxfb":
            self.first_url = 'http://www.stats.gov.cn/tjsj/zxfb/index.html'
            self.format_url = 'http://www.stats.gov.cn/tjsj/zxfb/index_{}.html'

        else:
            raise RuntimeError("请检查数据起始 url")
        
        # 对于可以一次加载完成的部分 采用的方式: 
        # self.browser = webdriver.Chrome()
        # self.browser = webdriver.Remote(
        #     command_executor="http://{}:4444/wd/hub".format(SELENIUM_HOST),
        #     desired_capabilities=DesiredCapabilities.CHROME
        # )
        # self.browser.implicitly_wait(30)  # 隐性等待，最长等30秒

        # 对于一次无法完全加载完整页面的情况 采用的方式: 
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "none"  # 懒加载模式，不等待页面加载完毕
        self.browser = webdriver.Chrome(desired_capabilities=capa)  # 关键!记得添加
        self.wait = WebDriverWait(self.browser, 5)  # 等待的最大时间 30 s

        self.sql_client = MyPymysqlPool(
            {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
            }
        )
        self.db = MYSQL_DB
        self.table = MYSQL_TABLE

        self.pages = ALL_PAGES

        self.pool = MqlPipeline(self.sql_client, self.db, self.table)

        # 出错的页面 
        self.error_list = []

        # 单独记录含有 table 的页面 方便单独更新和处理 
        self.links_have_table = []

    def crawl_list(self, offset):
        if offset == 0: 
            # print("要爬取的页面是{}".format(self.first_url))
            item_list = self.parse_list_page(self.first_url)
        else: 
            item_list = self.parse_list_page(self.format_url.format(offset))
        return item_list

    def parse_list_page(self, url):
        self.browser.get(url)
        ret = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='center_list']/ul[@class='center_list_contlist']")))   # 等待直到某个元素出现
        # print(ret.tag_name)  # ul
        lines = ret.find_elements_by_xpath("./li/a/*")
        item_list = []
        for line in lines: 
            item = {}
            link = line.find_element_by_xpath("./..").get_attribute("href")
            item['link'] = link 
            item['title'] = line.find_element_by_xpath("./font[@class='cont_tit03']").text
            item['pub_date'] = line.find_element_by_xpath("./font[@class='cont_tit02']").text
            # item['article'] = self.parse_detail_page(link)
            item_list.append(item)
            # print("在当前页面获取的数据是:" , item) 
        return item_list

    def parse_detail_page(self, url):
        # 在解析详情页的时间 遇到表格要避开 
        # 表格 for example:  http://www.stats.gov.cn/tjsj/zxfb/201910/t20191021_1704063.html 
        while True: 
            try: 
                self.browser.get(url)
                ret = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='TRS_PreAppend']")))   # 等待直到某个元素出现
                # print(ret.text)

                contents = []
                nodes = ret.find_elements_by_xpath("./*")

                for node in nodes: 
                    if not node.find_elements_by_xpath(".//table"): 
                        c = node.text 
                        if c: 
                            contents.append(c)
                    else: 
                        print("去掉 table 中的内容 ... ")
                # print("\n".join(contents))


                # self.browser.get(url)
                # ret = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='center_xilan']")))   # 等待直到某个元素出现
                # # print(ret.text)
                # # 判断页面正文中是否含有表格 

                # tables = ret.find_elements_by_xpath(".//table")
                # if tables: 
                #     self.links_have_table.append(url)



            except: 
                print("{} 出错重试 ... ".format(url))
            else: 
                break 
        
        # return ret.text
        return "\n".join(contents)

    def save_to_mysql(self, item):
        # 单个保存 
        self.pool.save_to_database(item)

    # def save_page(self, items: list):
    #     for item in items:
    #         self.save_to_mysql(item)

    def start(self):
        for page in range(0, self.pages):
            while True: 
                try:
                    # 总的来说 是先爬取到列表页 再根据列表页里面的链接去爬取详情页 
                    items = self.crawl_list(page)
                    # print(pprint.pformat(items)) 

                    for item in items: 
                        item['article'] = self.parse_detail_page(item['link'])
                        # print(pprint.pformat(item))
                        print()
                        print()
                        # time.sleep(3)
                        # self.save_to_mysql(item)
                        # print("保存成功 {}".format(item['link']))

                    # 按页保存
                    # self.save_page(page_list)
                    # print(pprint.pformat(page_list))
                except Exception as e:
                    logger.warning("加载出错了,重试, the page is {}".format(page))
                    # traceback.print_exc()
                else:
                    print("本页保存成功 {}".format(page))
                    break 

        self.browser.close()

    def create_table(self):
        sql = """
        DROP TABLE IF EXISTS `gov_stats_zxfb`;

        CREATE TABLE `gov_stats_zxfb` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime not null  COMMENT '发布时间',
          `title` varchar(64) collate utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(128) collate utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `article` text collate utf8_bin DEFAULT NULL COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`), 
          KEY `pub_date` (`pub_date`)
        ) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COMMENT='国家统计局[最新发布]'; 

        ALTER TABLE `gov_stats_zxfb` ADD unique(`link`); 

        show full columns from gov_stats_zxfb;
        """


if __name__ == "__main__":
    t1 = time.time()
    runner = GovStats()
    runner.start() 
    # print(runner.error_list) 
    # print(runner.links_have_table)
    t2 = time.time()
    print("花费的时间是 {} s".format(t2-t1))
