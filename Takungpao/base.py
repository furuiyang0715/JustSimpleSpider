import datetime
import os
import sys
import time
import traceback
from random import random

import requests
from gne import GeneralNewsExtractor

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base import SpiderBase, logger
from Takungpao.configs import (LOCAL, LOCAL_PROXY_URL, PROXY_URL)


class TakungpaoBase(SpiderBase):
    def __init__(self):
        super(TakungpaoBase, self).__init__()
        self.use_proxy = True
        self.extractor = GeneralNewsExtractor()
        self.fields = ['pub_date', 'link', 'title', 'article', 'source']
        self.table_name = 'Takungpao'
        self.by_the_time = datetime.datetime.today() - datetime.timedelta(days=2)

    def _get_proxy(self):
        """获取代理 IP"""
        if LOCAL:
            return requests.get(LOCAL_PROXY_URL).text.strip()
        else:
            random_num = random.randint(0, 10)
            if random_num % 2:
                time.sleep(1)
                return requests.get(PROXY_URL).text.strip()
            else:
                return requests.get(LOCAL_PROXY_URL).text.strip()

    def get(self, url):
        """底层为 requests 请求封装"""
        if not self.use_proxy:
            return requests.get(url, headers=self.headers)

        count = 0
        while True:
            count += 1
            if count > 10:
                return None
            try:
                proxy = {"proxy": self._get_proxy()}
                resp = requests.get(url, headers=self.headers, proxies=proxy)
            except:
                traceback.print_exc()
                time.sleep(0.5)
            else:
                if resp.status_code == 200:
                    return resp
                elif resp.status_code == 404:
                    return None
                else:
                    logger.warning("Status Code: {}".format(resp.status_code))
                    time.sleep(1)

    def convert_dt(self, time_stamp):
        """将时间戳转换为时间字符串"""
        d = str(datetime.datetime.fromtimestamp(time_stamp))
        return d

    def _process_pub_dt(self, pub_date):
        """对 pub_date 的各类时间格式进行统一"""
        current_dt = datetime.datetime.now()
        yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        after_yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        if "小时前" in pub_date:  # eg. 20小时前
            hours = int(pub_date.replace('小时前', ''))
            pub_date = (current_dt - datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        elif "昨天" in pub_date:  # eg. 昨天04:24
            pub_date = pub_date.replace('昨天', '')
            pub_date = " ".join([yesterday_dt_str, pub_date])
        elif '前天' in pub_date:  # eg. 前天11:33
            pub_date = pub_date.replace("前天", '')
            pub_date = " ".join([after_yesterday_dt_str, pub_date])
        else:  # eg. 02-29 04:24
            pub_date = str(current_dt.year) + '-' + pub_date
        return pub_date

    def _create_table(self):
        """大公报建表语句"""
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `source` varchar(20) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章来源',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大公报-财经类'; 
        '''.format(self.table_name)

        '''
        ALTER TABLE Takungpao ADD source varchar(20) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章来源';
        update Takungpao set source = '大公报'; 
        '''
        self._spider_init()
        self.spider_client.insert(sql)
        self.spider_client.end()
