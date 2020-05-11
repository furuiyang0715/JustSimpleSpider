# coding=utf8
import datetime
import logging
import os
import re
import sys
import time

import demjson
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from lxml import html

sys.path.append("./../")
from margin.configs import LOCAL
from margin.base import MarginBase, logger


class SHMarginSpider(MarginBase):
    """爬取当日的上交所融资融券列表
    网址: http://www.sse.com.cn/services/tradingservice/margin/info/againstmargin/
    更新时间: 当日即可更新当日数据
    更新内容: 目前[当日的]融资买入以及融券卖出列表
    爬虫表: margin_sh_list_spider
    更新时间: 每天的 3、9、15 点更新一次
    说明: 清单数据不可回溯历史。爬虫表时间是从部署上线时间 2020-05-11 开始的。
    """

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

    def __init__(self):
        super(SHMarginSpider, self).__init__()
        self.url = 'http://www.sse.com.cn/services/tradingservice/margin/info/againstmargin/'
        self.spider_table_name = 'margin_sh_list_spider'

    def start(self):
        """
        <li><a href="#tableData_961" data-toggle="tab">融资买入标的证券一览表
        </a></li><li><a href="#tableData_962" data-toggle="tab">融券卖出标的证券一览表
        </a></li><li><a href="#tableData_960" data-toggle="tab">融资融券可充抵保证金证券一览表
        """
        msg = ''
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

            msg += "{} 上交所的融券卖出标的爬虫入库成功\n".format(show_dt)

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

            msg += "{} 上交所的融资买入标的爬虫入库成功\n".format(show_dt)

            local_str = '本地测试:\n' if LOCAL else "远程:\n"
            local_str += msg

            # 关闭数据库连接
            try:
                spider.dispose()
            except:
                pass
            else:
                self.ding(local_str)

        else:
            raise Exception("网页请求失败")


def sh_list_task():
    now = lambda: time.time()
    start_dt = now()
    SHMarginSpider().start()
    logger.info("耗时: {} 秒".format(now() - start_dt))


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    # 确保重启时可以执行一次
    sh_list_task()

    scheduler.add_job(sh_list_task, 'cron', hour='3, 9, 15', max_instances=10, id="sh_spider_list_task")
    logger.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        logger.info(f"本次任务执行出错{e}")
        sys.exit(0)


# if __name__ == "__main__":
#     SHMarginSpider().start()

'''
docker build -f Dockerfile_shlist -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_list:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_list:v1
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_list:v1

# remote 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 -itd \
--env LOCAL=0 \
--name margin_sh_list \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_list:v1

# local
sudo docker run --log-opt max-size=10m --log-opt max-file=3 -itd \
--env LOCAL=1 \
--name margin_sh_list \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_list:v1 

'''
