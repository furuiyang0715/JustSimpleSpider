import datetime
import os
import sys
import time

import schedule

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, "../.."))
sys.path.insert(0, file_path)

from ExchangeMargin.configs import LOCAL
from ExchangeMargin.base import MarginBase, logger


class ShSync(MarginBase):
    """上交融资融券标的正式表记录生成
    思路: list spider 的时间是连续的, 在某一天将昨天和前天的数据进行 diff, 得到 to_add 和 to_delete。
    核对中发现: 将某只证券移出会出公告, 但是将其加入的时候不会。 因无法回溯历史列表，使用 detail 列表的 diff 替代。 存疑。
    运行时间: 在每天的 12 点运行
    """
    def __init__(self):
        super(ShSync, self).__init__()
        self.spider_table_name = 'margin_sh_list_spider'
        self.fields = ["SecuMarket", "InnerCode", "InDate", "OutDate", "TargetCategory", "TargetFlag", "ChangeReasonDesc"]

    def get_spider_latest_list(self, market, category):
        """获取爬虫库中最新的清单"""
        # self._spider_init()
        sql = '''select InnerCode from {} where ListDate = (select max(ListDate) from {} \
        where SecuMarket = {} and TargetCategory = {}) and SecuMarket = {} and TargetCategory = {}; 
        '''.format(self.spider_table_name, self.spider_table_name, market, category, market, category)
        # ret = self.spider_client.select_all(sql)
        ret = self.spider_conn.query(sql)
        ret = [r.get("InnerCode") for r in ret]
        return ret

    def get_spider_dt_list(self, dt, category):
        """获取爬虫库中具体某一天的清单"""
        # self._spider_init()
        sql_dt = '''select max(ListDate) as mx from {} where ListDate <= '{}' and SecuMarket =83 and TargetCategory = {}; 
        '''.format(self.spider_table_name, dt, category)
        # dt_ = self.spider_client.select_one(sql_dt).get("mx")
        dt_ = self.spider_conn.get(sql_dt).get("mx")
        logger.info("距离 {} 最近的之前的一天是{}".format(dt, dt_))
        if dt_:
            sql = '''select InnerCode from {} where ListDate = '{}' and SecuMarket = 83 and TargetCategory = {};
            '''.format(self.spider_table_name, dt_, category)
            ret = self.spider_conn.query(sql)
            ret = [r.get("InnerCode") for r in ret]
            return ret
        else:
            return []

    def _update(self, inner_code, dt, type, to_add):
        """
        数据库操作封装
        :param inner_code: 聚源内部编码
        :param dt: 变更发生时间
        :param type: 10 融资 20 融券
        :param to_add: 1 移入 0 移出
        :return:
        """
        # self._target_init()
        if to_add:  # 被列入的情况
            if type == 10:    # 融资
                item = {
                    "SecuMarket": 83,   # 上交所
                    "InnerCode": inner_code,  # 聚源内部编码
                    "InDate": dt,  # 被列入的时间
                    'TargetCategory': 10,   # 融资
                    'TargetFlag': 1,
                    'ChangeReasonDesc': None,
                    'UpdateTime': datetime.datetime.now(),
                }
            else:
                item = {
                    "SecuMarket": 83,
                    "InnerCode": inner_code,   # 聚源内部编码
                    "InDate": dt,
                    'TargetCategory': 20,   # 融券
                    'TargetFlag': 1,
                    'ChangeReasonDesc': None,
                    'UpdateTime': datetime.datetime.now(),
                }
            # count = self._save(self.target_client, item, self.target_table_name, self.fields)
            self.product_conn.table_insert(self.spider_table_name, item, self.fields)

        else:   # 被移出列表的情况
            if type == 10:    # 融资
                base_sql = '''update {} set OutDate = '{}', TargetFlag = 0 where SecuMarket = 83 and InnerCode = {}\
                and TargetCategory = 10  and TargetFlag = 1; '''
            else:    # 融券
                base_sql = '''update {} set OutDate = '{}', TargetFlag = 0 where SecuMarket = 83 and InnerCode = {}\
                and TargetCategory = 20  and TargetFlag = 1; '''

            sql = base_sql.format(self.target_table_name, dt, inner_code)
            count = self.product_conn.execute(sql)

    def start(self):
        msg = ''

        local_str = "本地测试: " if LOCAL else "远程: "
        msg += local_str
        msg += '上交所数据生成:\n'

        _today = datetime.datetime.combine(datetime.datetime.today(), datetime.time.min)
        _yester_day = _today - datetime.timedelta(days=1)
        _before_yester_day = _today - datetime.timedelta(days=2)
        print(_yester_day, "***", _before_yester_day)
        msg += '时间点: {} 与 {}\n'.format(_yester_day, _before_yester_day)
        _type_str_map = {
            10: "融资",
            20: "融券",
        }
        for _type in (10, 20):
            logger.info(_type)
            # 昨日的清单
            _yester_day_list = self.get_spider_dt_list(_yester_day, _type)
            # 前日的清单
            _before_yester_day_list = self.get_spider_dt_list(_before_yester_day, _type)
            print(len(_yester_day_list), len(_before_yester_day_list))

            if _yester_day and _before_yester_day:
                to_add = set(_yester_day_list) - set(_before_yester_day_list)
                to_delete = set(_before_yester_day_list) - set(_yester_day_list)
                logger.info("需新增数据: {}, 需删除数据: {}".format(to_add, to_delete))
                msg += "{}: 需新增数据: {}, 需删除数据: {}\n".format(_type_str_map.get(_type), to_add, to_delete)

                if to_add:
                    for one in to_add:
                        # 数据 时间 融资融券类型 移入移出类型
                        self._update(one, _yester_day, _type, 1)

                if to_delete:
                    for one in to_delete:
                        self._update(one, _yester_day, _type, 0)

        msg += '一致性检查: \n'

        # 状态计算清单
        dc_list_10 = set(sorted(self.product_dt_datas(83, 10)))
        # 真正清单
        spider_list_10 = set(sorted(self.get_spider_latest_list(83, 10)))
        msg += "融资一致性 check : dc_list - latest_list_spider >> {},latest_list_spider - dc_list>>{} \n".format(
            dc_list_10 - spider_list_10, spider_list_10 - dc_list_10)

        dc_list_20 = set(sorted(self.product_dt_datas(83, 20)))
        spider_list_20 = set(sorted(self.get_spider_latest_list(83, 20)))
        msg += "融券一致性 check : dc_list - latest_list_spider >> {},latest_list_spider - dc_list>>{} \n".format(
            dc_list_20 - spider_list_20, spider_list_20 - dc_list_20)

        print(msg)
        self.ding(msg)


def diff_task():
    try:
        ShSync().start()
    except:
        # TODO 异常处理
        pass


if __name__ == "__main__":
    diff_task()

    # schedule.every().day.at("12:00").do(diff_task)
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(10)


'''部署
docker build -f Dockerfile_shdiff -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_diff:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_diff:v1
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_diff:v1

# remote
sudo docker run --log-opt max-size=10m --log-opt max-file=3 -itd \
--env LOCAL=0 \
--name margin_sh_diff \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_diff:v1

# local
sudo docker run --log-opt max-size=10m --log-opt max-file=3 -itd \
--env LOCAL=1 \
--name margin_sh_diff \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/margin_sh_diff:v1
'''


'''删除的sql语句 
update  stk_mttargetsecurities set OutDate = '2020-07-01', TargetFlag = 0 where id in (10865, 10899); 

'''

'''新增的sql语句
260652 6.30 
233605  7.1 
select * from stk_mttargetsecurities where InnerCode in (260652, 233605) ; 
insert into stk_mttargetsecurities (SecuMarket, InnerCode, InDate,  TargetCategory, TargetFlag,  UpdateTime) values (83, 260652, '2020-06-30 00:00:00', 10, 1, '2020-07-01 16:00:02'); 
insert into stk_mttargetsecurities (SecuMarket, InnerCode, InDate,  TargetCategory, TargetFlag,  UpdateTime) values (83,  233605, '2020-07-01 00:00:00', 10, 1, '2020-07-01 16:00:01'); 

'''