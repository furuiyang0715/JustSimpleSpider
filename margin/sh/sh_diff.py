import datetime
import logging
import os
import sys
import time
from collections import Counter

from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append('./../')
from margin.configs import FIRST
from margin.base import MarginBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ShSync(MarginBase):
    """上交融资融券标的"""
    def __init__(self):
        self.juyuan_table_name = 'MT_TargetSecurities'
        self.target_table_name = 'stk_mttargetsecurities'
        # 爬虫库
        self.spider_table_name = 'margin_sh_list_spider'
        self.inner_code_map = self.get_inner_code_map()

    def show_juyuan_datas(self, juyuan=1):
        """
        分析聚源[正式库]已有的数据
        """
        if juyuan:
            table = self.juyuan_table_name
            client = self._init_pool(self.juyuan_cfg)
        else:
            table = self.target_table_name
            client = self._init_pool(self.product_cfg)
        # 上交所融资买入标的列表
        sql1 = '''select InnerCode from {} where TargetFlag = 1 and SecuMarket = 83 and TargetCategory = 10;'''.format(table)
        ret1 = client.select_all(sql1)
        ret1 = [r.get("InnerCode") for r in ret1]
        print(Counter(ret1))    # Counter({1346: 2, 1131: 1, 1133: 1, ...
        s_lst = set(self.get_spider_latest_list(83, 10))
        print(set(ret1) - s_lst)    # {1250, 2051, 1346, 1612, 1293, 1868, 1205, 2908, 1694}
        print(s_lst - set(ret1))    # {240096, 234476, 232095}

        # 上交所融券卖出标的列表
        sql2 = '''select InnerCode from {} where TargetFlag = 1 and SecuMarket = 83 and TargetCategory = 20;'''.format(table)
        ret2 = client.select_all(sql2)
        ret2 = [r.get("InnerCode") for r in ret2]
        print(Counter(ret2))  # Counter({1346: 2, 1131: 1, 1133: 1, 1154: 1, ..
        s_lst = set(self.get_spider_latest_list(83, 20))
        print(set(ret2) - s_lst)  # {1250, 2051, 1346, 1612, 1293, 1868, 1205, 2908, 1694}
        print(s_lst - set(ret2))  # {240096, 234476, 232095}

        print(set(ret1) == set(ret2))

        # # 查询聚源的最近更新时间
        # sql5 = '''select max(UpdateTime) as max_dt from MT_TargetSecurities ; '''
        # ret5 = juyuan.select_one(sql5).get("max_dt")
        # print(ret5)    # 2020-04-20 09:04:01

        '''TODO 需要在历史数据中进行查询的几个 
        mysql> select InnerCode, SecuCode, ChiName from secumain where InnerCode in (240096, 234476, 232095);
        +-----------+----------+-----------------------------------------------+
        | InnerCode | SecuCode | ChiName                                       |
        +-----------+----------+-----------------------------------------------+
        |    232095 | 688466   | 金科环境股份有限公司                          |
        |    234476 | 688365   | 杭州光云科技股份有限公司                      |
        |    240096 | 688318   | 深圳市财富趋势科技股份有限公司                |
        +-----------+----------+-----------------------------------------------+
        3 rows in set (0.01 sec)
        TODO  这几个最近更新进去的 似乎只会发移出公告 而不会发列入公告 .. 
    
        '''

        '''只能从历史的交易明细中尝试找一下列入日期 
        select * from margin_sh_detail_spider where InnerCode = '232095' order by ListDate ;    # 2020-05-08 00:00:00 
        select * from margin_sh_detail_spider where InnerCode = '234476' order by ListDate ;    # 2020-04-29 00:00:00 
        select * from margin_sh_detail_spider where InnerCode = '240096' order by ListDate ;    # 2020-04-27 00:00:00 
        '''

        client.dispose()

    def parse_detail(self):
        """根据历史明细生成数据"""
        self._update("232095", datetime.datetime(2020, 5, 8), 1, 1)
        self._update("232095", datetime.datetime(2020, 5, 8), 2, 1)

        self._update("234476", datetime.datetime(2020, 4, 29), 1, 1)
        self._update("234476", datetime.datetime(2020, 4, 29), 2, 1)

        self._update("240096", datetime.datetime(2020, 4, 27), 1, 1)
        self._update("240096", datetime.datetime(2020, 4, 27), 2, 1)

        # TODO  待明细信息出具后观察
        self._update("226097", datetime.datetime(2020, 5, 11), 1, 1)
        self._update("226097", datetime.datetime(2020, 5, 11), 2, 1)

    def get_spider_latest_list(self, market, category):
        """获取爬虫库中最新的清单"""
        # ['SecuMarket', 'InnerCode', 'SecuCode', 'SecuAbbr', 'SerialNumber', 'ListDate', 'TargetCategory']
        spider = self._init_pool(self.spider_cfg)
        sql = '''select InnerCode from {} where ListDate = (select max(ListDate) from {} \
        where SecuMarket = {} and TargetCategory = {}) and SecuMarket = {} and TargetCategory = {}; 
        '''.format(self.spider_table_name, self.spider_table_name, market, category, market, category)
        ret = spider.select_all(sql)
        ret = [r.get("InnerCode") for r in ret]
        return ret

    def get_spider_dt_list(self, dt, category):
        """获取爬虫库中具体某一天的清单"""
        spider = self._init_pool(self.spider_cfg)

        sql_dt = '''select max(ListDate) as mx from {} where ListDate <= '{}' and SecuMarket =83 and TargetCategory = {}; 
        '''.format(self.spider_table_name, dt, category)
        dt_ = spider.select_one(sql_dt).get("mx")
        logger.info("距离 {} 最近的之前的一天是{}".format(dt, dt_))
        if dt_:
            sql = '''select InnerCode from {} where ListDate = '{}' and SecuMarket = 83 and TargetCategory = {};
            '''.format(self.spider_table_name, dt_, category)
            ret = spider.select_all(sql)
            ret = [r.get("InnerCode") for r in ret]
            return ret
        else:
            return []

    def parse_announcement(self):
        """从公告中提取更改信息 """
        # 公告链接地址: http://www.sse.com.cn/disclosure/magin/announcement/

        # 在聚源的最大更新时间之后的有：
        # (1) 4.23 的公告: http://www.sse.com.cn/disclosure/magin/announcement/ssereport/c/c_20200423_5052948.shtml
        # 内容: 在2020年4月24日将天津松江（600225） 调出融资融券标的证券名单
        inner_code = self.get_inner_code('600225')
        # print(inner_code)  # 1346
        self._update(inner_code, datetime.datetime(2020, 4, 24), 1, 0)
        self._update(inner_code, datetime.datetime(2020, 4, 24), 2, 0)

        # (2) 4.28 的公告: http://www.sse.com.cn/disclosure/magin/announcement/ssereport/c/c_20200428_5067981.shtml
        # 内容: 在2020年4月29日将 博信股份（600083） 调出融资融券标的证券名单
        inner_code = self.get_inner_code("600083")
        # print(inner_code)   # 1205
        self._update(inner_code, datetime.datetime(2020, 4, 29), 1, 0)
        self._update(inner_code, datetime.datetime(2020, 4, 29), 2, 0)

        # (3）4.29 的公告: http://www.sse.com.cn/disclosure/magin/announcement/ssereport/c/c_20200429_5075757.shtml
        # 内容: 于2020年4月30日将 交大昂立（600530）和宏图高科（600122）调出融资融券标的证券名单
        inner_code_1 = self.get_inner_code('600530')
        inner_code_2 = self.get_inner_code('600122')
        # print(inner_code_1, inner_code_2)  # 1694 1250
        self._update(inner_code_1, datetime.datetime(2020, 4, 30), 1, 0)
        self._update(inner_code_1, datetime.datetime(2020, 4, 30), 2, 0)

        self._update(inner_code_2, datetime.datetime(2020, 4, 30), 1, 0)
        self._update(inner_code_2, datetime.datetime(2020, 4, 30), 2, 0)

        # (4) 4.30 的公告:http://www.sse.com.cn/disclosure/magin/announcement/ssereport/c/c_20200430_5085195.shtml
        # 内容: 于2020年5月6日将 美都能源（600175）、六国化工（600470）、飞乐音响（600651）、安信信托（600816）和宜华生活（600978）调出融资融券标的证券名单。
        in_co_1 = self.get_inner_code('600175')
        in_co_2 = self.get_inner_code('600470')
        in_co_3 = self.get_inner_code('600651')
        in_co_4 = self.get_inner_code('600816')
        in_co_5 = self.get_inner_code('600978')
        # print(in_co_1, in_co_2, in_co_3, in_co_4, in_co_5)  # 1293 1612 1868 2051 2908
        for in_co in (in_co_1, in_co_2, in_co_3, in_co_4, in_co_5):
            self._update(in_co, datetime.datetime(2020, 5, 6), 1, 0)
            self._update(in_co, datetime.datetime(2020, 5, 6), 2, 0)

    def _update(self, inner_code, dt, type, to_add):
        """

        :param inner_code: 聚源内部编码
        :param dt: 变更发生时间
        :param type: 1 融资 0 融券
        :param to_add: 1 移入 0 移出
        :return:
        """
        # 正式库表的字段
        fields = ["SecuMarket", "InnerCode", "InDate", "OutDate", "TargetCategory", "TargetFlag", "ChangeReasonDesc"]
        target = self._init_pool(self.product_cfg)
        if to_add:  # 被列入的情况
            if type == 1:    # 融资
                item = {
                    "SecuMarket": 83,   # 上交所
                    "InnerCode": inner_code,
                    "InDate": dt,  # 被列入的时间
                    'TargetCategory': 10,   # 融资
                    'TargetFlag': 1,
                    'ChangeReasonDesc': '',
                    'UpdateTime': datetime.datetime.now(),
                }
            else:
                item = {
                    "SecuMarket": 83,
                    "InnerCode": inner_code,
                    "InDate": dt,
                    'TargetCategory': 20,   # 融券
                    'TargetFlag': 1,
                    'ChangeReasonDesc': '',
                    'UpdateTime': datetime.datetime.now(),
                }
            count = self._save(target, item, self.target_table_name, fields)
            logger.info("type: {}, add 记录条数 {}".format(type, count))
        else:   # 被移出列表的情况
            if type == 1:    # 融资
                base_sql = '''update {} set OutDate = '{}', TargetFlag = 2 where SecuMarket = 83 and InnerCode = {}\
                and TargetCategory = 10  and TargetFlag = 1; '''
            else:    # 融券
                base_sql = '''update {} set OutDate = '{}', TargetFlag = 2 where SecuMarket = 83 and InnerCode = {}\
                and TargetCategory = 20  and TargetFlag = 1; '''

            sql = base_sql.format(self.target_table_name, dt, inner_code)
            ret = target.update(sql)
            logger.info("type: {}, update 记录条数是 {}".format(type, ret))

        try:
            target.dispose()
        except:
            logger.warning("dispose error")
            raise

    def start(self):
        # 临时解析公告 只在首次运行
        if FIRST:
            self.show_juyuan_datas()
            self.parse_announcement()
            self.parse_detail()
            self.show_juyuan_datas(juyuan=0)

        _today = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)
        _yester_day = _today - datetime.timedelta(days=1)
        _before_yester_day = _today - datetime.timedelta(days=2)
        print(_yester_day, "***", _before_yester_day)
        for _type in (10, 20):
            _yester_day_list = self.get_spider_dt_list(_yester_day, _type)
            _before_yester_day_list = self.get_spider_dt_list(_before_yester_day, _type)
            print(_yester_day_list, _before_yester_day_list)
            if _yester_day and _before_yester_day:
                to_add = set(_yester_day_list) - set(_before_yester_day_list)
                to_delete = set(_before_yester_day_list) - set(_yester_day_list)
                if to_add:
                    for one in to_add:
                        self._update(one, _yester_day, _type, 1)
                if to_delete:
                    for one in to_delete:
                        self._update(one, _yester_day, _type, 0)


def diff_task():
    """对比两天清单差异的任务"""
    now = lambda: time.time()
    start_time = now()
    ShSync().start()
    logger.info(f"用时: {now() - start_time} 秒")    # (end)大概是 80s (dispose)大概是 425s


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    # 确保重启时可以执行一次
    diff_task()

    scheduler.add_job(diff_task, 'cron', hour='16, 23', max_instances=10, id="sh_diff_task")
    logger.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        logger.info(f"本次任务执行出错{e}")
        sys.exit(0)

'''部署
docker build -f Dockerfile_shdiff -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_diff:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_diff:v1 
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_diff:v1 

# remote 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 -itd \
--env LOCAL=0 \
--env FIRST=0 \
--name margin_sh_diff \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_diff:v1  

# local
sudo docker run --log-opt max-size=10m --log-opt max-file=3 -itd \
--env LOCAL=1 \
--env FIRST=0 \
--name margin_sh_diff \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_diff:v1  

'''
