import datetime
import json
import logging
import pprint
import random
import re
import string
import sys
import time
import traceback
from urllib.parse import urlencode

import pymysql
import requests as req
from gne import GeneralNewsExtractor

from PublicOpinion.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL, LOCAL_MYSQL_HOST, \
    LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, LOCAL_MYSQL_DB
from PublicOpinion.sql_pool import PyMysqlPoolBase

logger = logging.getLogger()


class CNStock(object):
    def __init__(self, *args, **kwargs):
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 "
                                 "(KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
                   "Referer": "http://news.cnstock.com/news/sns_yw/index.html",
                   }
        self.headers = headers
        self.list_url = "http://app.cnstock.com/api/waterfall?"
        self.extractor = GeneralNewsExtractor()
        self.local = LOCAL
        if self.local:
            conf = {
                "host": LOCAL_MYSQL_HOST,
                "port": LOCAL_MYSQL_PORT,
                "user": LOCAL_MYSQL_USER,
                "password": LOCAL_MYSQL_PASSWORD,
                "db": LOCAL_MYSQL_DB,

            }
            self.db = LOCAL_MYSQL_DB
        else:
            conf = {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
                "db": MYSQL_DB,
            }
            self.db = MYSQL_DB

        self.sql_pool = PyMysqlPoolBase(**conf)
        self.table = "cn_stock"
        self.error_list = []
        self.error_detail = []
        self.topic = kwargs.get("topic")
        self.check_date = datetime.datetime.today() - datetime.timedelta(days=1)

    def make_query_params(self, page):
        """
        拼接动态请求参数
        """
        query_params = {
            # 'colunm': 'qmt-sns_yw',
            'colunm': self.topic,
            'page': str(page),   # 最大 50 页
            'num': str(10),
            'showstock': str(0),
            'callback': 'jQuery{}_{}'.format(
                ''.join(random.choice(string.digits) for i in range(0, 20)),
                str(int(time.time() * 1000))
            ),
            '_': str(int(time.time() * 1000)),
        }
        return query_params

    def get_list(self):
        for page in range(0, 1000):
            print(page)
            params = self.make_query_params(page)
            url = self.list_url + urlencode(params)
            # print(url)
            ret = req.get(url, headers=self.headers).text
            # print(ret)

            json_data = re.findall(r'jQuery\d{20}_\d{13}\((\{.*?\})\)', ret)[0]
            # print(json_data)

            py_data = json.loads(json_data)
            # print(py_data)

            datas = py_data.get("data", {}).get("item")
            if not datas:
                break
            for one in datas:
                item = dict()
                pub_date = datetime.datetime.strptime(one.get("time"), "%Y-%m-%d %H:%M:%S")
                # print(pub_date)
                if pub_date < self.check_date:
                    print("增量完毕\n")
                    return

                item['pub_date'] = pub_date
                item['title'] = one.get("title")
                item['link'] = one.get("link")
                yield item

    def get_detail(self, detail_url):
        page = req.get(detail_url, headers=self.headers).text
        result = self.extractor.extract(page)
        content = result.get("content")
        return content

    def contract_sql(self, to_insert):
        """
        根据待插入字典 拼接出对应的 sql 语句
        """
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}`.`{}` '''.format(
            self.db, self.table) + fields_str + ''' values ''' + values_str + ''';'''
        return base_sql, tuple(vs)

    def _save(self, to_insert):
        try:
            insert_sql, values = self.contract_sql(to_insert)
            count = self.sql_pool.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            logger.warning("重复")
            return 1
        except:
            traceback.print_exc()
            logger.warning("失败")
        else:
            return count

    def __del__(self):
        print("释放资源... ")
        try:
            self.sql_pool.dispose()
        except:
            pass

    def start(self):
        count = 0
        for item in self.get_list():
            # print(item, type(item))
            if item:
                link = item.get('link')
                if not link or link == "null":
                    continue
                item['article'] = self.get_detail(link)
                print(item)
                ret = self._save(item)
                count += 1
                if ret:
                    # print("insert ok ")
                    pass
                else:
                    self.error_detail.append(item.get("link"))
                    # print("insert fail")

                if count > 10:
                    self.sql_pool.connection.commit()
                    # print("提交")
                    count = 0


if __name__ == "__main__":
    # runner = CNStock(topic='qmt-sns_yw')   #  要闻-宏观
    # runner = CNStock(topic='qmt-sns_jg')   # 要闻-金融

    # runner = CNStock(topic="qmt-scp_gsxw")   # 公司-公司聚焦
    # runner = CNStock(topic="qmt-tjd_ggkx")   # 公司-公告快讯
    # runner = CNStock(topic="qmt-tjd_bbdj")   # 公司-公告解读

    # runner = CNStock(topic="qmt-smk_gszbs")   # 市场-直播
    # runner = CNStock(topic="qmt-sx_xgjj")   # 市场-新股-新股聚焦
    # runner = CNStock(topic="qmt-sx_zcdt")   # 市场-新股-政策动态
    # runner = CNStock(topic="qmt-sx_xgcl")   # 市场-新股-新股策略
    # runner = CNStock(topic="qmt-sx_ipopl")   # 市场-新股-IPO评论

    # runner = CNStock(topic="qmt-smk_jjdx")   # 市场-基金
    # runner = CNStock(topic="qmt-sns_qy")   # 市场-券业
    # runner = CNStock(topic="qmt-smk_zq")   # 市场-债券
    # runner = CNStock(topic="qmt-smk_xt")   # 市场-信托

    # runner = CNStock(topic="qmt-skc_tt")   # 科创板-要闻
    # runner = CNStock(topic="qmt-skc_jgfx")   # 科创板-监管
    # runner = CNStock(topic="qmt-skc_sbgsdt")   # 科创板-公司
    # runner = CNStock(topic="qmt-skc_tzzn")   # 科创板-投资
    # runner = CNStock(topic="qmt-skc_gd")   # 科创板-观点
    runner = CNStock(topic="qmt-sjrz_yw")   # 新三板-要闻

    # 测试解析详情页可以实现自动翻页
    # ret = runner.get_detail("http://ggjd.cnstock.com/company/scp_ggjd/tjd_ggjj/202002/4489878.htm")
    # print(ret)
    runner.start()
