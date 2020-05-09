import datetime

from margin.base import MarginBase

'''聚源库\目标库\历史记录库
mysql> select * from MT_TargetSecurities limit 1;
+--------------+------------+-----------+---------------------+---------+----------------+------------+------------------+---------------------+--------------+
| ID           | SecuMarket | InnerCode | InDate              | OutDate | TargetCategory | TargetFlag | ChangeReasonDesc | UpdateTime          | JSID         |
+--------------+------------+-----------+---------------------+---------+----------------+------------+------------------+---------------------+--------------+
| 325373670171 |         90 |         3 | 2010-03-31 00:00:00 | NULL    |             10 |          1 | NULL             | 2018-10-17 15:30:38 | 593105438229 |
+--------------+------------+-----------+---------------------+---------+----------------+------------+------------------+---------------------+--------------+
1 row in set (0.01 sec)


mysql> select * from MT_TargetSecurities limit 1;
+----+------------+-----------+---------------------+---------+----------------+------------+------------------+---------------------+---------------------+---------------------+
| id | SecuMarket | InnerCode | InDate              | OutDate | TargetCategory | TargetFlag | ChangeReasonDesc | UpdateTime          | CREATETIMEJZ        | UPDATETIMEJZ        |
+----+------------+-----------+---------------------+---------+----------------+------------+------------------+---------------------+---------------------+---------------------+
|  1 |         90 |         3 | 2010-03-31 00:00:00 | NULL    |             10 |          1 | NULL             | 2018-10-17 15:30:38 | 2020-05-07 14:41:30 | 2020-05-07 14:41:30 |
+----+------------+-----------+---------------------+---------+----------------+------------+------------------+---------------------+---------------------+---------------------+
1 row in set (0.02 sec)


mysql> select * from sz_margin_history limit 1;
+----+------------+-----------+----------+--------------+--------------+---------------------+-------------+-----------------+--------------+-------------------+-------------------+---------------------+---------------------+
| id | SecuMarket | InnerCode | SecuCode | SecuAbbr     | SerialNumber | ListDate            | FinanceBool | FinanceBuyToday | SecurityBool | SecuritySellToday | SecuritySellLimit | CREATETIMEJZ        | UPDATETIMEJZ        |
+----+------------+-----------+----------+--------------+--------------+---------------------+-------------+-----------------+--------------+-------------------+-------------------+---------------------+---------------------+
|  1 |         90 |         3 | 000001   | 深发展Ａ     |            1 | 2010-03-29 00:00:00 |           1 |               0 |            1 |                 0 |                 0 | 2020-05-08 14:16:11 | 2020-05-08 14:16:11 |
+----+------------+-----------+----------+--------------+--------------+---------------------+-------------+-----------------+--------------+-------------------+-------------------+---------------------+---------------------+
1 row in set (0.01 sec)

'''


class Checker(MarginBase):
    def __init__(self):
        self.juyuan_table_name = 'MT_TargetSecurities'
        # 聚源数据库最后的更新时间点
        self.juyuan_last_day = datetime.datetime(2020, 4, 19)
        self.sz_history_table_name = 'sz_margin_history'

    def check1(self):
        # 查询聚源最新的数据
        juyuan = self._init_pool(self.juyuan_cfg)
        sql = '''select InnerCode from {} where SecuMarket = 90 and TargetCategory = 10 and TargetFlag = 1; '''.format(self.juyuan_table_name)
        ret1 = juyuan.select_all(sql)
        ret1 = sorted(set([r.get("InnerCode") for r in ret1]))
        print(ret1)
        print(len(ret1))

        # 查询 sz 的历史数据
        spider = self._init_pool(self.spider_cfg)
        sql1 = '''select max(ListDate) as mx from {} where ListDate <= '{}'; '''.format(self.sz_history_table_name, self.juyuan_last_day)
        dt = spider.select_one(sql1).get("mx")
        sql = '''select InnerCode from {} where ListDate = '{}' and  FinanceBool = 1; '''.format(self.sz_history_table_name, dt)   # and FinanceBuyToday = 1
        ret2 = spider.select_all(sql)
        ret2 = sorted(set([r.get("InnerCode") for r in ret2]))

        print(ret2)
        print(len(ret2))
        print(set(ret1) - set(ret2))    # {204806}
        print(set(ret2) - set(ret1))    # set()

    def dt_datas(self, dt1):
        spider = self._init_pool(self.spider_cfg)
        sql_dt = '''select max(ListDate) as mx from {} where ListDate <= '{}'; '''.format(self.sz_history_table_name, dt1)
        dt1_ = spider.select_one(sql_dt).get("mx")
        sql = '''select InnerCode from {} where ListDate = '{}' and  FinanceBool = 1; '''.format(self.sz_history_table_name, dt1_)  # and FinanceBuyToday = 1
        ret1 = spider.select_all(sql)
        ret1 = sorted(set([r.get("InnerCode") for r in ret1]))
        return ret1

    def diff_dts(self, dt1: datetime.datetime, dt2: datetime.datetime):
        # dt1 = datetime.datetime(2020, 4, 15)
        data1 = self.dt_datas(dt1)
        data1 = set(sorted(data1))

        # dt2 = datetime.datetime(2020, 4, 18)
        data2 = self.dt_datas(dt2)
        data2 = set(sorted(data2))

        print(data1 == data2)
        print(data1 - data2)
        print(data2 - data1)

    def check2(self):
        # 较新的时间点 之前的数据点
        # self.diff_dts(datetime.datetime(2020, 4, 16), datetime.datetime(2020, 4, 15))
        # self.diff_dts(datetime.datetime(2020, 4, 29), datetime.datetime(2020, 4, 28))
        # self.diff_dts(datetime.datetime(2020, 4, 30), datetime.datetime(2020, 4, 29))
        # self.diff_dts(datetime.datetime(2020, 5, 6), datetime.datetime(2020, 5, 5))

        pass


if __name__ == "__main__":
    # Checker().check1()

    Checker().check2()

    pass
