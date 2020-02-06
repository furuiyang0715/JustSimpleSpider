import datetime
import logging
import math
import pprint
import time
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.parse import urlencode
import pymongo

import sys

from taoguba.common.sqltools.mysql_pool import MyPymysqlPool, MqlPipeline
from taoguba.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_TABLE

sys.path.append("./../")
from taoguba.parse_tools import ParseSpider
from taoguba.dc_base import DCSpider
from taoguba.proxy_spider import ProxySpider
from taoguba.common.proxy_tools.proxy_pool import QueueProxyPool

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TaogubaSpider(DCSpider, ProxySpider, ParseSpider):
    demo_keys = {
        'sz000651': '格力电器', 'sz002051': '中工国际', 'sz002052': '同洲电子',
        'sh601001': '大同煤业', 'sh601988': '中国银行', 'sz002054': '德美化工',
        'sz002055': '得润电子', 'sz002056': '横店东磁', 'sh600048': '保利发展',
        'sz002057': '中钢天源', 'sz002058': '威尔泰', 'sz002059': '云南旅游',
        'sh601006': '大秦铁路', 'sz002060': '二局股份', 'sz002061': '浙江交科'

    }

    def __init__(self):
        # 淘股吧的起始爬取的列表页
        self.list_url = "https://www.taoguba.com.cn/quotes/getStockUpToDate?"
        # 每次请求返回的个数 不要设置太大 对对方服务器造成太大压力
        self.perPageNum = 100
        # 因数据量比较大 将数据存入 mongo 数据库中 或者是在测试时使用
        # self.mon = pymongo.MongoClient("127.0.0.1:27018").pach.taoguba
        self.mon = pymongo.MongoClient("192.168.0.101:27018").pach.taoguba
        self.ip_pool = QueueProxyPool()

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
        self.pool = MqlPipeline(self.sql_client, self.db, self.table)

        self.error_detail = []
        self.error_list = []

    def save_to_mysql(self, item):
        self.pool.save_to_database(item)
        logger.info("插入成功 ")

    def insert_list_info(self, item):
        try:
            self.mon.insert_one(item)
        except pymongo.errors.DuplicateKeyError:
            logger.warning("重复插入数据 {}".format(item['articleUrl']))
        except Exception:
            traceback.print_exc()

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

    def get_strategy_model(self, item):
        taoguba_model = {}

        # 对时间类型的数据进行处理
        acdt = item.get("actionDate")
        new_acdt = datetime.datetime.fromtimestamp(float(acdt)/1000).strftime("%Y-%m-%d %H:%M:%S")
        taoguba_model.update({"actionDate": new_acdt})

        # 对 stockAttr 进行处理
        stoa = item.get("stockAttr")
        new_stoa = ",".join([r.get("stockCode") for r in stoa])
        taoguba_model.update({"stockAttr": new_stoa})

        # 对字符串以及文本类型的数据进行处理
        # for field in ("stockCode", "ChiNameAbbr", "body", "subject", "userName", "gnName",  "articleUrl", "articleContent"):
        for field in ("body", "subject", "articleContent"):
            new_value = self.transferContent(item.get(field))
            if new_value:
                new_value = new_value.replace("&nbsp;", " ")
            taoguba_model.update({field: new_value})

        return taoguba_model

    def select_topic_from_mongo(self, code):
        """
        从 mongo 数据库中获取指定股票的待爬取详情
        :param code:
        :return:
        """
        cursor = self.mon.find({"stockCode": code}, {"_id": 0})
        for item in cursor:
            detail_link = item.get("articleUrl")
            if detail_link:
                try:
                    logger.debug("开始解析详情页 {}".format(detail_link))
                    content = self.parse_detail(item)
                    item['articleContent'] = content
                    to_insert = self.get_strategy_model(item)
                    self.save_to_mysql(to_insert)
                    logger.info("{} --> {}".format(item['stockCode'], content[:100]))
                except:
                    traceback.print_exc()
                    self.error_detail.append(detail_link)
                    logger.debug("解析详情页失败 ")

    def start_requests(self, demo_keys):
        for code, name in demo_keys.items():
        # for code, name in self.lowerkeys.items():
            logger.info(f"code: {code}, name: {name}")
            item = {}
            # 股票代码以及中文简称
            item["stockCode"] = code
            item['ChiNameAbbr'] = name
            tstamp = int(time.time()) * 1000  # js 中的时间戳 第一次这个值选用当前时间
            query_params = self.make_query_params(code, tstamp)
            # 拼接出某只股票的起始 url
            start_url = self.list_url + urlencode(query_params)
            logger.info(f"股票 {name} 的起始 url 是 {start_url}")
            self.parse_list(code, name, start_url)


if __name__ == "__main__":
    t = TaogubaSpider()
    # # 将全部的列表页 url 采集到 mongodb 数据库中
    all_keys = sorted(list(t.lowerkeys.items()))
    # print(len(all_keys))  # 3919

    group_length = math.ceil(len(all_keys) / 500)
    # print(group_length)  # 8
    t.start_requests(dict(all_keys[15:]))

    sys.exit(0)
    # # 查看采集是失败的页面
    # print('采集失败的详情页是'.format(t.error_detail))
    # print('采集失败的列表页是'.format(t.error_list))
    # 采集全部的详情页页面 并将其插入到 mysql 数据库中
    # for code in t.demo_keys:
    #     print(code)
    #     t.select_topic_from_mongo(code)

    # 实施步骤
    # （1） 将全部的列表页多线程爬取一遍 存入 mongo 数据库
    #  (2)  从mysql中获取已经爬取过的链接
    # （3） 求差集, 将未爬取的连接插入数据库中

    # from concurrent.futures import ThreadPoolExecutor
    # import time


    def spider(keys):
        TaogubaSpider().start_requests(keys)


    with ThreadPoolExecutor(max_workers=5) as t:  # 创建一个最大容纳数量为5的线程池

        task1 = t.submit(spider, dict(all_keys[:800]))  # 通过submit提交执行的函数到线程池中
        task2 = t.submit(spider, dict(all_keys[800:1600]))
        task3 = t.submit(spider, dict(all_keys[1600:2400]))
        task4 = t.submit(spider, dict(all_keys[2400:3200]))
        task5 = t.submit(spider, dict(all_keys[3200:]))

        # print(f"task1: {task1.done()}")  # 通过done来判断线程是否完成
        time.sleep(2.5)
        # print(f"task1: {task1.done()}")
        print(task1.result())  # 通过result来获取返回值
        print(task2.result())  # 通过result来获取返回值
        print(task3.result())  # 通过result来获取返回值
        print(task4.result())  # 通过result来获取返回值
        print(task5.result())  # 通过result来获取返回值

