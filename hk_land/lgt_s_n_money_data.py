import datetime
import json
import pprint
import re
import requests as req
import logging

from hk_land.configs import LOCAL, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, \
    LOCAL_MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from hk_land.sql_pool import PyMysqlPoolBase

logging.basicConfig(level=logging.DEBUG,
                    filename='output.log',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s')

logger = logging.getLogger(__name__)


class EMLGTNanBeiXiangZiJin(object):
    def __init__(self):
        # http://data.eastmoney.com/hsgtcg/gzcglist.html
        self.url = '''
        http://push2.eastmoney.com/api/qt/kamt.rtmin/get?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55,f56&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery18306854619522421488_1566280636697&_=1566284477196'''
        self.south_table_name = 'lgt_south_money_data'
        self.north_table_name = 'lgt_north_money_data'
        self.local = LOCAL

    def get_response_data(self):
        page = req.get(self.url).text
        data = re.findall(r"jQuery\d{20}_\d{13}\((.*)\)", page)[0]
        py_data = json.loads(data).get('data')
        return py_data

    def _init_pool(self):
        if self.local:
            conf = {
                "host": LOCAL_MYSQL_HOST,
                "port": LOCAL_MYSQL_PORT,
                "user": LOCAL_MYSQL_USER,
                "password": LOCAL_MYSQL_PASSWORD,
                "db": LOCAL_MYSQL_DB,
            }
        else:
            conf = {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
                "db": MYSQL_DB,
            }
        self.sql_pool = PyMysqlPoolBase(**conf)

    def process_n2s(self, py_data):
        """处理陆港通南向数据"""
        n2s = py_data.get("n2s")
        n2s_date = py_data.get("n2sDate")
        _cur_year = datetime.datetime.now().year   # FIXME 不太严谨
        _cur_moment_str = str(_cur_year) + "-" + n2s_date

        for data_str in n2s:
            data = data_str.split(",")
            item = dict()
            dt_moment = _cur_moment_str + " " + data[0]
            item['Date'] = dt_moment  # 时间点 补全当天的完整时间
            item['HKHFlow'] = data[1] if data[1] != '-' else 0  # 港股通（沪）南向资金流
            item['HKHBalance'] = data[2] if data[2] != "-" else 0  # 港股通(沪) 当日资金余额
            item['HKZFlow'] = data[3] if data[3] != "-" else 0  # 港股通(深) 南向资金流
            item['HKZBalance'] = data[4] if data[4] != "-" else 0  # 港股通(深) 当日资金余额
            item['SouthMoney'] = data[5] if data[5] != "-" else 0  # 南向资金
            item['Category'] = '南向资金'
            print(item)
            # self.save(item)

    def process_s2n(self, py_data):
        """处理陆港通北向数据"""
        s2n = py_data.get("s2n")
        s2n_date = py_data.get("s2nDate")
        _cur_year = datetime.datetime.now().year   # FIXME 不太严谨
        _cur_moment_str = str(_cur_year) + "-" + s2n_date

        for data_str in s2n:
            data = data_str.split(",")
            item = dict()
            dt_moment = _cur_moment_str + " " + data[0]
            item['Date'] = dt_moment  # 时间点 补全当天的完整时间
            item['SHFlow'] = data[1] if data[1] != "-" else 0  # 沪股通 北上资金流
            item['SHBalance'] = data[2] if data[2] != "-" else 0  #
            item['SZFlow'] = data[3] if data[3] != '-' else 0
            item['SZBalance'] = data[4] if data[4] != '-' else 0
            item['NorthMoney'] = data[5] if data[5] != '-' else 0
            item['Category'] = '北向资金'
            print(item)
            # self.save(item)

    def _create_table(self):
        sql_n = '''
        CREATE TABLE IF NOT EXISTS `lgt_north_money_data` (
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
        '''

        sql_s = '''
         CREATE TABLE IF NOT EXISTS `lgt_south_money_data` (
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
        '''
        self.sql_pool.insert(sql_n)
        self.sql_pool.insert(sql_s)
        self.sql_pool.end()

    def _start(self):
        self._init_pool()
        self._create_table()
        py_data = self.get_response_data()
        logger.info("开始处理陆港通北向数据")
        self.process_s2n(py_data)

        print()
        print()

        logger.info("开始处理陆港通南向数据")
        self.process_n2s(py_data)

    def __del__(self):
        try:
            self.sql_pool.dispose()
        except:
            pass


if __name__ == "__main__":
    eml = EMLGTNanBeiXiangZiJin()
    eml._start()
