# coding=utf8
import datetime
import json
import logging
import re
import sys
import traceback

import demjson
import requests
from lxml import html

sys.path.append("./../")
from margin.configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD,
                            SPIDER_MYSQL_DB, PRODUCT_MYSQL_HOST, PRODUCT_MYSQL_PORT, PRODUCT_MYSQL_USER,
                            PRODUCT_MYSQL_PASSWORD, PRODUCT_MYSQL_DB, JUY_HOST, DC_PASSWD, DC_DB, DC_HOST,
                            DC_PORT, DC_USER, JUY_PORT, JUY_USER, JUY_PASSWD, JUY_DB)
from margin.sql_pool import PyMysqlPoolBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SHMarginSpider(object):
    spider_cfg = {   # 爬虫库
        "host": SPIDER_MYSQL_HOST,
        "port": SPIDER_MYSQL_PORT,
        "user": SPIDER_MYSQL_USER,
        "password": SPIDER_MYSQL_PASSWORD,
        "db": SPIDER_MYSQL_DB,
    }

    product_cfg = {    # 正式库
        "host": PRODUCT_MYSQL_HOST,
        "port": PRODUCT_MYSQL_PORT,
        "user": PRODUCT_MYSQL_USER,
        "password": PRODUCT_MYSQL_PASSWORD,
        "db": PRODUCT_MYSQL_DB,
    }
    
    # 聚源数据库
    juyuan_cfg = {
        "host": JUY_HOST,
        "port": JUY_PORT,
        "user": JUY_USER,
        "password": JUY_PASSWD,
        "db": JUY_DB,
    }

    # 数据中心库
    dc_cfg = {
        "host": DC_HOST,
        "port": DC_PORT,
        "user": DC_USER,
        "password": DC_PASSWD,
        "db": DC_DB,
    }

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

    def _drop_table(self):
        """临时删除数据库"""
        sql = '''drop table {}; '''.format(self.spider_table_name)
        spider = self._init_pool(self.spider_cfg)
        spider.insert(sql)
        spider.dispose()

    def _create_table(self):
        """创建爬虫数据库"""
        # fields = ['SecuMarket', 'InnerCode', 'SecuCode', 'SecuAbbr', 'SerialNumber', 'ListDate', 'TargetCategory']
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
          `SecuMarket` int(11) DEFAULT NULL COMMENT '证券市场',
          `InnerCode` int(11) NOT NULL COMMENT '证券内部编码',
          `SecuCode` varchar(10) DEFAULT NULL COMMENT '证券代码',
          `SecuAbbr` varchar(200) DEFAULT NULL COMMENT '证券简称',
          `SerialNumber` int(10) DEFAULT NULL COMMENT '网站清单序列号',
          `ListDate` datetime NOT NULL COMMENT '列入时间',
          `TargetCategory` int(11) NOT NULL COMMENT '标的类别',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `un2` (`SecuMarket`, `TargetCategory`,`ListDate`, `InnerCode`) USING BTREE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='融资融券标的证券清单';
        '''.format(self.spider_table_name)
        spider = self._init_pool(self.spider_cfg)
        spider.insert(sql)
        spider.dispose()

    def contract_sql(self, to_insert: dict, table: str, update_fields: list):
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}` '''.format(table) + fields_str + ''' values ''' + values_str
        on_update_sql = ''' ON DUPLICATE KEY UPDATE '''
        update_vs = []
        for update_field in update_fields:
            on_update_sql += '{}=%s,'.format(update_field)
            update_vs.append(to_insert.get(update_field))
        on_update_sql = on_update_sql.rstrip(",")
        sql = base_sql + on_update_sql + """;"""
        vs.extend(update_vs)
        return sql, tuple(vs)

    def _save(self, sql_pool, to_insert, table, update_fields):
        try:
            insert_sql, values = self.contract_sql(to_insert, table, update_fields)
            count = sql_pool.insert(insert_sql, values)
        except:
            traceback.print_exc()
            logger.warning("失败")
        else:
            if count == 1:    # 插入新数据的时候结果为 1
                logger.info("插入新数据 {}".format(to_insert))

            elif count == 2:
                logger.info("刷新数据 {}".format(to_insert))

            else:   # 数据已经存在的时候结果为 0
                # logger.info(count)
                # logger.info("已有数据 {} ".format(to_insert))
                pass

            sql_pool.end()
            return count

    def get_inner_code_map(self):
        """
        获取聚源内部编码映射表
        https://dd.gildata.com/#/tableShow/27/column///
        https://dd.gildata.com/#/tableShow/718/column///
        """
        juyuan = self._init_pool(self.juyuan_cfg)

        # if self.type in ("sh", "sz"):
        #     sql = 'SELECT SecuCode,InnerCode from SecuMain WHERE SecuCategory in (1, 2) and SecuMarket in (83, 90) and ListedSector in (1, 2, 6, 7);'
        # else:
        #     sql = '''SELECT SecuCode,InnerCode from hk_secumain WHERE SecuCategory in (51, 3, 53, 78) and SecuMarket in (72) and ListedSector in (1, 2, 6, 7);'''

        # 8 是开放式基金
        sql = 'SELECT SecuCode,InnerCode from SecuMain WHERE SecuCategory in (1, 2, 8) and SecuMarket in (83, 90) and ListedSector in (1, 2, 6, 7);'
        ret = juyuan.select_all(sql)
        juyuan.dispose()
        info = {}
        for r in ret:
            key = r.get("SecuCode")
            value = r.get('InnerCode')
            info[key] = value
        return info

    def get_inner_code(self, secu_code):
        ret = self.inner_code_map.get(secu_code)
        if not ret:
            logger.warning("{} 不存在内部编码".format(secu_code))
            raise
        return ret

    def __init__(self):
        self.url = 'http://www.sse.com.cn/services/tradingservice/margin/info/againstmargin/'
        self.spider_table_name = 'targetsecurities'
        self.inner_code_map = self.get_inner_code_map()

    def start(self):
        """
        <li><a href="#tableData_961" data-toggle="tab">融资买入标的证券一览表
        </a></li><li><a href="#tableData_962" data-toggle="tab">融券卖出标的证券一览表
        </a></li><li><a href="#tableData_960" data-toggle="tab">融资融券可充抵保证金证券一览表
        """
        # self._drop_table()
        self._create_table()
        resp = requests.get(self.url)
        if resp.status_code == 200:
            page = resp.text.encode("ISO-8859-1").decode("utf-8")
            doc = html.fromstring(page)

            fields = ['SecuMarket', 'InnerCode', 'SecuCode', 'SecuAbbr', 'SerialNumber', 'ListDate', 'TargetCategory']
            spider = self._init_pool(self.spider_cfg)

            # 962
            datas = doc.xpath("//div[@class='table-responsive sse_table_T01 tdclickable']/table[@class='table search_']/script[@type='text/javascript']")[0].text
            table_datas = re.findall('''tableData\['tableData_962'\] = (.*);''', datas, re.DOTALL)[0]
            py_datas = demjson.decode(table_datas)
            show_date = py_datas.get("staticDate")
            show_dt = datetime.datetime.combine(datetime.datetime.strptime(show_date, "%Y-%m-%d %H:%M:%S"), datetime.time.min)
            list_datas = py_datas.get("list")
            lst_datas = []
            for data in list_datas:
                if data:
                    lst_datas.append(data)
            for data in lst_datas:
                item = dict()
                item['SerialNumber'] = int(data[0])    # str
                item['SecuAbbr'] = data[2]
                item['ListDate'] = show_dt
                # 标的类别：10-融资买入标的，20-融券卖出标的
                item['TargetCategory'] = 20
                item['SecuMarket'] = 83
                secu_code = data[1].strip()
                item['SecuCode'] = secu_code
                inner_code = self.get_inner_code(secu_code)
                item['InnerCode'] = inner_code
                self._save(spider, item, self.spider_table_name, fields)

            # 961
            datas = doc.xpath("//table[@class='table search_bdzqkc search3T']/script[@type='text/javascript']")[0].text
            show_dt = datetime.datetime.strptime(re.findall("var showdate = '(.*)'", datas)[0], "%Y%m%d")
            table_datas = re.findall('''tableData\['tableData_961'\] = (.*);''', datas, re.DOTALL)[0]
            py_datas = demjson.decode(table_datas)
            list_datas = py_datas.get("list")
            lst_datas = []
            for data in list_datas:
                if data:
                    lst_datas.append(data)
            # 编号 证券代码 证券简称
            # [['1', '510050 ', '50ETF '], ['2', '510180 ', '180ETF '], ...
            for data in lst_datas:
                item = dict()
                item['SerialNumber'] = int(data[0])
                item['SecuAbbr'] = data[2]
                item['ListDate'] = show_dt
                # 标的类别：10-融资买入标的，20-融券卖出标的
                item['TargetCategory'] = 10
                item['SecuMarket'] = 83
                secu_code = data[1].strip()
                item['SecuCode'] = secu_code
                inner_code = self.get_inner_code(secu_code)
                item['InnerCode'] = inner_code
                self._save(spider, item, self.spider_table_name, fields)

            # 关闭数据库连接
            try:
                spider.dispose()
            except:
                pass


if __name__ == "__main__":
    SHMarginSpider().start()
