import datetime
import re
import time
import traceback
import logging

import demjson
import pymysql
import requests
from gne import GeneralNewsExtractor

import sys
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
sys.path.append('./../')

from PublicOpinion.configs import (MYSQL_HOST, MYSQL_PORT, MYSQL_PASSWORD, MYSQL_USER, MYSQL_DB, LOCAL,
                                   LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD,
                                   LOCAL_MYSQL_DB, LOCAL_PROXY_URL, PROXY_URL)
from PublicOpinion.sql_pool import PyMysqlPoolBase
import PublicOpinion.tools as tools


class Money163(object):
    if LOCAL:
        spider_cfg = {
            "host": LOCAL_MYSQL_HOST,
            "port": LOCAL_MYSQL_PORT,
            "user": LOCAL_MYSQL_USER,
            "password": LOCAL_MYSQL_PASSWORD,
            "db": LOCAL_MYSQL_DB,
        }
    else:
        spider_cfg = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "db": MYSQL_DB,
        }

    def __init__(self):
        self.list_url = "http://money.163.com/special/00251G8F/news_json.js"
        self.extractor = GeneralNewsExtractor()
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 "
                                 "(KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",}

        self.table = "netease_money"
        self.error_detail = []

    def _init_pool(self, cfg: dict):
        """
        eg.
        conf = {
                "host": LOCAL_MYSQL_HOST,
                "port": LOCAL_MYSQL_PORT,
                "user": LOCAL_MYSQL_USER,
                "password": LOCAL_MYSQL_PASSWORD,
                "db": LOCAL_MYSQL_DB,
        }
        :param cfg:
        :return:
        """
        pool = PyMysqlPoolBase(**cfg)
        return pool

    def _parse_list(self, body):
        js_obj = re.findall(r"news:(.*)\};", body)[0]
        py_obj = demjson.decode(js_obj)
        for type in py_obj:  # 得到每一个子主题
            for data in type:
                yield data

    def _parse_detail(self, detail_url):
        try:
            page = requests.get(detail_url, headers=self.headers).text
            result = self.extractor.extract(page)
            content = result.get("content")
        except:
            return
        return content

    def contract_sql(self, to_insert):
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}` '''.format(self.table) + fields_str + ''' values ''' + values_str + ''';'''
        return base_sql, tuple(vs)

    def _save(self, to_insert, client):
        try:
            insert_sql, values = self.contract_sql(to_insert)
            count = client.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            return 1
        except:
            traceback.print_exc()
        else:
            logger.info("更入新数据 {}".format(to_insert))
            client.end()
            return count

    def get_proxy(self):
        if LOCAL:
            return requests.get(LOCAL_PROXY_URL).text.strip()
        else:
            return requests.get(PROXY_URL).text.strip()

    def get_list_resp(self):
        count = 0
        while True:
            proxy = self.get_proxy()
            print(">> ", proxy)
            try:
                list_resp = requests.get(self.list_url,
                                         proxies={"http": proxy},
                                         timeout=3)
            except:
                count += 1
                if count > 10:
                    return
                time.sleep(1)
            else:
                if list_resp.status_code != 200:
                    count += 1
                    if count > 10:
                        return
                    time.sleep(1)
                else:
                    break
        return list_resp

    def start(self):
        count = 3
        while True:
            try:
                self._start()
            except:
                count -= 1
                if count < 0:
                    traceback.print_exc()
                    tools.ding_msg("网易财经 {} 数据爬取失败".format(self.table))
                else:
                    traceback.print_exc()
                    print("网易财经失败重试中 ")
            else:
                break

    def _create_table(self):
        client = self._init_pool(self.spider_cfg)
        sql = '''
        CREATE TABLE IF NOT EXISTS `netease_money` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='网易财经'; 
        '''
        client.insert(sql)
        client.dispose()

    def _start(self):
        self._create_table()
        list_resp = self.get_list_resp()
        logger.info("list resp: {}".format(list_resp))
        if list_resp and list_resp.status_code == 200:
            body = list_resp.text
            ret = list(self._parse_list(body))
            count = 0
            client = self._init_pool(self.spider_cfg)
            for one in ret:
                item = dict()
                link = one.get("l")
                item['link'] = link
                item['title'] = one.get("t")
                pub_date = one.get("p")
                item['pub_date'] = pub_date
                article = self._parse_detail(one.get("l"))

                if article:
                    item['article'] = article
                    ret = self._save(item, client)
                    if not ret:
                        self.error_detail.append(link)
                    else:
                        count += 1
                else:
                    self.error_detail.append(link)
            try:
                client.dispose()
            except:
                pass
            logger.info("爬取失败的链接列表是{}".format(self.error_detail))


if __name__ == "__main__":
    m = Money163()
    m.start()
