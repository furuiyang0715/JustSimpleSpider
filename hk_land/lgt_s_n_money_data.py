import datetime
import hashlib
import json
import logging
import re
import traceback

from decimal import Decimal
import requests as req

from hk_land.configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER, SPIDER_MYSQL_PASSWORD,
                             SPIDER_MYSQL_DB, PRODUCT_MYSQL_HOST, PRODUCT_MYSQL_PORT, PRODUCT_MYSQL_USER,
                             PRODUCT_MYSQL_PASSWORD, PRODUCT_MYSQL_DB)
from hk_land.sql_pool import PyMysqlPoolBase


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EMLGTNanBeiXiangZiJin(object):
    """陆股通实时数据"""

    spider_cfg = {
        "host": SPIDER_MYSQL_HOST,
        "port": SPIDER_MYSQL_PORT,
        "user": SPIDER_MYSQL_USER,
        "password": SPIDER_MYSQL_PASSWORD,
        "db": SPIDER_MYSQL_DB,
    }

    product_cfg = {
        "host": PRODUCT_MYSQL_HOST,
        "port": PRODUCT_MYSQL_PORT,
        "user": PRODUCT_MYSQL_USER,
        "password": PRODUCT_MYSQL_PASSWORD,
        "db": PRODUCT_MYSQL_DB,
    }

    def __init__(self):
        self.url = '''
        http://push2.eastmoney.com/api/qt/kamt.rtmin/get?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55,f56&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery18306854619522421488_1566280636697&_=1566284477196'''
        self.south_table_name = 'lgt_south_money_data'
        self.north_table_name = 'lgt_north_money_data'
        self.product_table_name = 'hkland_flow'

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

    def get_response_data(self):
        page = req.get(self.url).text
        data = re.findall(r"jQuery\d{20}_\d{13}\((.*)\)", page)[0]
        py_data = json.loads(data).get('data')
        return py_data

    def select_n2s_datas(self):
        """获取已有的南向数据"""
        spider = self._init_pool(self.spider_cfg)
        start_dt = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
        end_dt = datetime.datetime.combine(datetime.datetime.now(), datetime.time.max)
        sql = '''select * from {} where Date >= '{}' and Date <= '{}';'''.format(
            self.south_table_name, start_dt, end_dt)
        south_datas = spider.select_all(sql)
        spider.dispose()
        for data in south_datas:
            data.pop("CREATETIMEJZ")
            data.pop("UPDATETIMEJZ")
        return south_datas

    def select_s2n_datas(self):
        """获取已有的北向数据"""
        spider = self._init_pool(self.spider_cfg)
        start_dt = datetime.datetime.combine(datetime.datetime.now(), datetime.time.min)
        end_dt = datetime.datetime.combine(datetime.datetime.now(), datetime.time.max)
        sql = '''select * from {} where Date >= '{}' and Date <= '{}';'''.format(
            self.north_table_name, start_dt, end_dt)
        north_datas = spider.select_all(sql)
        spider.dispose()
        for data in north_datas:
            data.pop("CREATETIMEJZ")
            data.pop("UPDATETIMEJZ")
        return north_datas

    def process_n2s(self, py_data):
        """处理陆港通南向数据"""
        n2s = py_data.get("n2s")
        n2s_date = py_data.get("n2sDate")
        _cur_year = datetime.datetime.now().year   # FIXME 不太严谨
        _cur_moment_str = str(_cur_year) + "-" + n2s_date
        logger.info("获取到的南向数据的时间是 {}".format(_cur_moment_str))

        items = []
        for data_str in n2s:
            data = data_str.split(",")
            item = dict()
            dt_moment = _cur_moment_str + " " + data[0]
            item['Date'] = datetime.datetime.strptime(dt_moment, "%Y-%m-%d %H:%M")  # 时间点 补全当天的完整时间
            item['HKHFlow'] = Decimal(data[1]) if data[1] != '-' else 0  # 港股通（沪）南向资金流
            item['HKHBalance'] = Decimal(data[2]) if data[2] != "-" else 0  # 港股通(沪) 当日资金余额
            item['HKZFlow'] = Decimal(data[3]) if data[3] != "-" else 0  # 港股通(深) 南向资金流
            item['HKZBalance'] = Decimal(data[4]) if data[4] != "-" else 0  # 港股通(深) 当日资金余额
            item['SouthMoney'] = Decimal(data[5]) if data[5] != "-" else 0  # 南向资金
            item['Category'] = '南向资金'
            items.append(item)

        to_delete = []
        to_insert = []

        already_sourth_datas = self.select_n2s_datas()
        for r in already_sourth_datas:
            d_id = r.pop("id")
            if not r in items:
                to_delete.append(d_id)

        for r in items:
            if not r in already_sourth_datas:
                to_insert.append(r)

        update_fields = ['HKHFlow', 'HKHBalance', 'HKZFlow', 'HKZBalance', 'SouthMoney']

        for item in to_insert:
            self._save(item,  self.south_table_name, update_fields)

    def process_s2n(self, py_data):
        """处理陆港通北向数据"""
        s2n = py_data.get("s2n")
        s2n_date = py_data.get("s2nDate")
        _cur_year = datetime.datetime.now().year   # FIXME 不太严谨
        _cur_moment_str = str(_cur_year) + "-" + s2n_date
        logger.info("获取到的北向数据的时间是 {}".format(_cur_moment_str))

        items = []
        for data_str in s2n:
            data = data_str.split(",")
            item = dict()
            dt_moment = _cur_moment_str + " " + data[0]
            item['Date'] = datetime.datetime.strptime(dt_moment, "%Y-%m-%d %H:%M")  # 时间点 补全当天的完整时间
            item['SHFlow'] = Decimal(data[1]) if data[1] != "-" else 0  # 沪股通 北上资金流
            item['SHBalance'] = Decimal(data[2]) if data[2] != "-" else 0  #
            item['SZFlow'] = Decimal(data[3]) if data[3] != '-' else 0
            item['SZBalance'] = Decimal(data[4]) if data[4] != '-' else 0
            item['NorthMoney'] = Decimal(data[5]) if data[5] != '-' else 0
            item['Category'] = '北向资金'
            items.append(item)

        to_delete = []
        to_insert = []

        already_north_datas = self.select_s2n_datas()
        for r in already_north_datas:
            d_id = r.pop("id")
            if not r in items:
                to_delete.append(d_id)

        for r in items:
            if not r in already_north_datas:
                to_insert.append(r)

        update_fields = ['SHFlow', 'SHBalance', 'SZFlow', 'SZBalance', 'NorthMoney']

        for item in to_insert:
            self._save(item, self.north_table_name, update_fields)

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

    # def contract_sql(self, to_insert: dict, table: str):
    #     ks = []
    #     vs = []
    #     for k in to_insert:
    #         ks.append(k)
    #         vs.append(to_insert.get(k))
    #     fields_str = "(" + ",".join(ks) + ")"
    #     values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
    #     base_sql = '''REPLACE INTO `{}` '''.format(table) + fields_str + ''' values ''' + values_str + ''';'''
    #     return base_sql, tuple(vs)

    def _save(self, to_insert, table, update_fields: list):
        spider = self._init_pool(self.spider_cfg)
        try:
            insert_sql, values = self.contract_sql(to_insert, table, update_fields)
            count = spider.insert(insert_sql, values)
        except:
            traceback.print_exc()
            logger.warning("失败")
            count = None
        else:
            logger.info("更入新数据 {}".format(to_insert))
        finally:
            spider.dispose()
        return count

    def _create_table(self):
        spider = self._init_pool(self.spider_cfg)
        sql_n = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
          `Date` datetime NOT NULL COMMENT '日期',
          `SHFlow` decimal(19,4) DEFAULT NULL COMMENT '沪股通当日资金流向(万）',
          `SHBalance` decimal(19,4) DEFAULT NULL COMMENT '沪股通当日资金余额（万）',
          `SZFlow` decimal(19,4) DEFAULT NULL COMMENT '深股通当日资金流向(万）',
          `SZBalance` decimal(19,4) DEFAULT NULL COMMENT '深股通当日资金余额（万）',
          `NorthMoney` decimal(19,4) DEFAULT NULL COMMENT '北向资金',
          `Category` varchar(20) COLLATE utf8_bin DEFAULT NULL COMMENT '类别',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `unique_key` (`Date`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='陆股通-北向资金-东财'; 
        '''.format(self.north_table_name)

        sql_s = '''
         CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
          `Date` datetime NOT NULL COMMENT '日期',
          `HKHFlow` decimal(19,4) DEFAULT NULL COMMENT '港股通（沪）当日资金流向(万）',
          `HKHBalance` decimal(19,4) DEFAULT NULL COMMENT '港股通（沪）当日资金余额（万）',
          `HKZFlow` decimal(19,4) DEFAULT NULL COMMENT '港股通（深）当日资金流向(万）',
          `HKZBalance` decimal(19,4) DEFAULT NULL COMMENT '港股通（深）当日资金余额（万）',
          `SouthMoney` decimal(19,4) DEFAULT NULL COMMENT '南向资金',
          `Category` varchar(20) COLLATE utf8_bin DEFAULT NULL COMMENT '类别',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `unique_key` (`Date`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='陆股通-南向资金-东财'; 
        '''.format(self.south_table_name)

        spider.insert(sql_n)
        spider.insert(sql_s)
        spider.end()

    def _start(self):
        self._create_table()
        py_data = self.get_response_data()
        logger.info("开始处理陆港通北向数据")
        self.process_s2n(py_data)

        logger.info("开始处理陆港通南向数据")
        self.process_n2s(py_data)

    def start(self):
        try:
            self._start()
        except:
            traceback.print_exc()

    # >>>>> 数据加工处理分割线

    def sync_south(self):
        start_time = datetime.datetime.now() - datetime.timedelta(days=12)
        end_time = datetime.datetime.now()
        fields_map = {
            "Date": "DateTime",
            "HKHFlow": "ShHkFlow",
            "HKHBalance": "ShHkBalance",
            "HKZFlow": "SzHkFlow",
            'HKZBalance': "SzHkBalance",
            'SouthMoney': "Netinflow",
            "ID": "CMFID",
            "UPDATETIMEJZ": "CMFTime",
        }
        as_str = "select "
        for key, value in fields_map.items():
            as_str += "{} as {},".format(key, value)

        as_str = as_str.strip(",")
        as_str += " from {} where Date > '{}' and Date < '{}'; ".format(self.south_table_name, start_time, end_time)
        spider = self._init_pool(self.spider_cfg)
        south_datas = spider.select_all(as_str)
        spider.dispose()
        return south_datas

    def sync_north(self):
        start_time = datetime.datetime.now() - datetime.timedelta(days=12)
        end_time = datetime.datetime.now()
        fields_map = {
            "Date": "DateTime",
            "SHFlow": "ShHkFlow",
            "SHBalance": "ShHkBalance",
            "SZFlow": "SzHkFlow",
            'SZBalance': "SzHkBalance",
            'NorthMoney': "Netinflow",
            "ID": "CMFID",
            "UPDATETIMEJZ": "CMFTime",
        }
        as_str = "select "
        for key, value in fields_map.items():
            as_str += "{} as {},".format(key, value)

        as_str = as_str.strip(",")
        as_str += " from {} where Date > '{}' and Date < '{}'; ".format(self.north_table_name, start_time, end_time)
        spider = self._init_pool(self.spider_cfg)
        north_datas = spider.select_all(as_str)
        spider.dispose()
        return north_datas

    def hash_row(self, data):
        values = sorted([str(value) for value in data.values()])
        hash_str = ''
        for value in values:
            hash_str += value
        md5 = hashlib.md5()
        md5.update(hash_str.encode())
        hash_value = md5.hexdigest()
        data["HashID"] = hash_value
        return data

    def _create_pro_table(self):
        """创建正式库的表"""
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
          `DateTime` datetime NOT NULL COMMENT '交易时间',
          `ShHkFlow` decimal(19,4) NOT NULL COMMENT '沪股通/港股通(沪)当日资金流向(万）',
          `ShHkBalance` decimal(19,4) NOT NULL COMMENT '沪股通/港股通(沪)当日资金余额（万）',
          `SzHkFlow` decimal(19,4) NOT NULL COMMENT '深股通/港股通(深)当日资金流向(万）',
          `SzHkBalance` decimal(19,4) NOT NULL COMMENT '深股通/港股通(深)当日资金余额（万）',
          `Netinflow` decimal(19,4) NOT NULL COMMENT '南北向资金,当日净流入',
          `Category` tinyint(4) NOT NULL COMMENT '类别:1 南向, 2 北向',
          `HashID` varchar(50) COLLATE utf8_bin DEFAULT NULL COMMENT '哈希ID',
          `CMFID` bigint(20) unsigned DEFAULT NULL COMMENT '源表来源ID',
          `CMFTime` datetime DEFAULT NULL COMMENT 'Come From Time',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `unique_key2` (`DateTime`,`Category`),
          UNIQUE KEY `unique_key` (`CMFID`, `Category`),
          KEY `DateTime` (`DateTime`) USING BTREE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='陆港通-实时资金流向';
        '''.format(self.product_table_name)
        product = self._init_pool(self.product_cfg)
        product.insert(sql)
        product.dispose()

    def psave(self, to_insert, table, update_fields):
        product = self._init_pool(self.product_cfg)
        try:
            insert_sql, values = self.contract_sql(to_insert, table, update_fields)
            count = product.insert(insert_sql, values)
        except:
            traceback.print_exc()
            logger.warning("失败")
            count = None
        else:
            if count != 0:
                logger.info("更入新数据 {}".format(to_insert))
        finally:
            product.dispose()
        return count

    def sync(self):
        self._create_pro_table()
        south_datas = self.sync_south()
        update_fields = ['DateTime', 'ShHkFlow', 'ShHkBalance', 'SzHkFlow', 'SzHkBalance', 'Netinflow', 'Category', 'HashID']
        for data in south_datas:
            self.hash_row(data)
            data['Category'] = 1
            self.psave(data, self.product_table_name, update_fields)

        north_datas = self.sync_north()
        for data in north_datas:
            self.hash_row(data)
            data['Category'] = 2
            self.psave(data, self.product_table_name, update_fields)


if __name__ == "__main__":
    eml = EMLGTNanBeiXiangZiJin()
    eml.start()
    eml.sync()
