import datetime

from ExchangeMargin.base import MarginBase

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

        self.sh_list_table_name = 'margin_sh_list_spider'
        self.sh_detail_table_name = 'margin_sh_detail_spider'

        self.target_table_name = 'stk_mttargetsecurities'

    def juyuan_latest(self, market=90):
        # 查询聚源最新的数据
        juyuan = self._init_pool(self.juyuan_cfg)
        sql = '''select InnerCode from {} where SecuMarket = {} and TargetCategory = 10 and TargetFlag = 1; '''.format(self.juyuan_table_name, market)
        ret1 = juyuan.select_all(sql)
        ret1 = sorted(set([r.get("InnerCode") for r in ret1]))
        print(ret1)
        print(len(ret1))
        return ret1

    # def check_1(self):
    #     # 查询 sz list 在聚源最后一天的情况
    #     spider = self._init_pool(self.spider_cfg)
    #     sql1 = '''select max(ListDate) as mx from {} where ListDate <= '{}'; '''.format(self.sz_history_table_name, self.juyuan_last_day)
    #     dt = spider.select_one(sql1).get("mx")
    #     sql = '''select InnerCode from {} where ListDate = '{}' and  FinanceBool = 1; '''.format(self.sz_history_table_name, dt)   # and FinanceBuyToday = 1
    #     ret2 = spider.select_all(sql)
    #     ret2 = sorted(set([r.get("InnerCode") for r in ret2]))
    #     return ret2

    def check_2(self):
        # 较新的时间点 之前的数据点
        # self.diff_dts(datetime.datetime(2020, 4, 16), datetime.datetime(2020, 4, 15))
        # self.diff_dts(datetime.datetime(2020, 4, 29), datetime.datetime(2020, 4, 28))
        # self.diff_dts(datetime.datetime(2020, 4, 30), datetime.datetime(2020, 4, 29))
        # self.diff_dts(datetime.datetime(2020, 5, 6), datetime.datetime(2020, 5, 5))
        pass

    def sz_dt_datas(self, dt1, _type=1):
        spider = self._init_pool(self.spider_cfg)
        sql_dt = '''select max(ListDate) as mx from {} where ListDate <= '{}'; 
        '''.format(self.sz_history_table_name, dt1)
        dt1_ = spider.select_one(sql_dt).get("mx")
        if dt1_:
            sql = '''select InnerCode from {} where ListDate = '{}' and  FinanceBool = {}; 
            '''.format(self.sz_history_table_name, dt1_, _type)  # and FinanceBuyToday = 1
            ret1 = spider.select_all(sql)
            ret1 = sorted(set([r.get("InnerCode") for r in ret1]))
            return ret1
        else:
            return []

    def sz_diff_dts(self, dt1: datetime.datetime, dt2: datetime.datetime):
        # dt1 = datetime.datetime(2020, 4, 15)
        data1 = self.sz_dt_datas(dt1)
        data1 = set(sorted(data1))

        # dt2 = datetime.datetime(2020, 4, 18)
        data2 = self.sz_dt_datas(dt2)
        data2 = set(sorted(data2))

        print(data1 == data2)
        print(data1 - data2)
        print(data2 - data1)

    def sz_check(self):
        r1 = set(sorted(self.sz_dt_datas(datetime.datetime(2020, 5, 8), 1)))
        print(r1)
        p1 = set(sorted(self.product_dt_datas(90, 10)))
        print(p1)
        print(r1 - p1)
        print(p1 - r1)    # {204806}

        pass

    # #############################################################################################
    # sh
    def sh_dt_datas(self, dt, _category):
        """

        :param dt:
        :param _type:
        :return:
        """
        spider = self._init_pool(self.spider_cfg)
        sql_dt = '''select max(ListDate) as mx from {} where ListDate <= '{}'; 
        '''.format(self.sh_list_table_name, dt)
        dt1_ = spider.select_one(sql_dt).get("mx")
        sql = '''select InnerCode from {} where ListDate = '{}' and TargetCategory = {}; 
        '''.format(self.sh_list_table_name, dt1_, _category)
        ret1 = spider.select_all(sql)
        ret1 = sorted(set([r.get("InnerCode") for r in ret1]))
        return ret1

    def product_dt_datas(self, market, category):
        """

        :param market:
        :param category:
        :return:
        """
        # TODO 测试以及正式库
        # clinet = self._init_pool(self.product_cfg)
        clinet = self._init_pool(self.dc_cfg)
        sql = '''select InnerCode from {} where SecuMarket = {} and TargetCategory = {} and TargetFlag = 1; 
        '''.format(self.target_table_name, market, category)
        ret = clinet.select_all(sql)
        ret = [r.get("InnerCode") for r in ret]
        return ret

    def sh_list_spider_product_check(self):
        r1 = sorted(self.sh_dt_datas(datetime.datetime(2020, 5, 11), 10))
        p1 = sorted(self.product_dt_datas(83, 10))
        print(r1 == p1)

        r2 = sorted(self.sh_dt_datas(datetime.datetime(2020, 5, 11), 20))
        p2 = sorted(self.product_dt_datas(83, 20))
        print(r2 == p2)


if __name__ == "__main__":
    Checker().sz_check()




    pass
