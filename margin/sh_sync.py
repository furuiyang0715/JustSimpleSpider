import logging
import sys
import time
from collections import Counter

from margin.base import MarginBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ShSync(MarginBase):
    """上交融资融券标的"""
    def __init__(self):
        self.juyuan_table_name = 'MT_TargetSecurities'
        self.target_table_name = 'MT_TargetSecurities'
        # 爬虫库
        self.spider_table_name = 'targetsecurities'
        self.inner_code_map = self.get_inner_code_map()

    def load_juyuan(self):
        """将聚源已有的数据导入"""
        select_fields = ['SecuMarket', 'InnerCode', 'InDate', 'OutDate', 'TargetCategory', 'TargetFlag', 'ChangeReasonDesc',
                         'UpdateTime',
                         # 'JSID',
                         ]
        select_str = ",".join(select_fields).rstrip(",")
        juyuan = self._init_pool(self.juyuan_cfg)
        sql = '''select {} from {};'''.format(select_str, self.juyuan_table_name)
        ret = juyuan.select_all(sql)
        juyuan.dispose()

        update_fields = ['SecuMarket', 'InnerCode', 'InDate', 'OutDate', 'TargetCategory', 'TargetFlag', 'ChangeReasonDesc', 'UpdateTime']
        target = self._init_pool(self.product_cfg)
        for item in ret:
            self._save(target, item, self.target_table_name, update_fields)

        try:
            target.dispose()
        except Exception as e:
            logger.warning(f"dispose error: {e}")

    def show_juyuan_datas(self):
        """
        分析聚源已有的数据
        """
        juyuan = self._init_pool(self.juyuan_cfg)
        # 上交所融资买入标的列表
        sql1 = '''select InnerCode from MT_TargetSecurities where TargetFlag = 1 and SecuMarket = 83 and TargetCategory = 10;'''
        ret1 = juyuan.select_all(sql1)
        ret1 = [r.get("InnerCode") for r in ret1]
        # print(ret1)
        # print(len(ret1), len(set(ret1)))
        print(Counter(ret1))    # Counter({1346: 2, 1131: 1, 1133: 1, ...

        s_lst = set(self.get_spider_latest_list(83, 10))
        print(set(ret1) - s_lst)
        print(s_lst - set(ret1))

        sys.exit(0)



        # 上交所融券卖出标的列表
        sql2 = '''select InnerCode from MT_TargetSecurities where TargetFlag = 1 and SecuMarket = 83 and TargetCategory = 20;'''
        ret2 = juyuan.select_all(sql2)
        ret2 = [r.get("InnerCode") for r in ret2]
        # print(ret2)
        # print(len(ret2), len(set(ret2)))
        print(Counter(ret2))  # Counter({1346: 2, 1131: 1, 1133: 1, 1154: 1, ..
        print(set(ret1) == set(ret2))

        # 深交所融资买入标的
        sql3 = '''select InnerCode from MT_TargetSecurities where TargetFlag = 1 and SecuMarket = 90 and TargetCategory = 10;'''
        ret3 = juyuan.select_all(sql3)
        ret3 = [r.get("InnerCode") for r in ret3]
        # print(ret3)
        # print(len(ret3), len(set(ret3)))
        print(Counter(ret3))   # Counter({12243: 2, 16175: 2, 3: 1, 6: 1, 83: 1, 102: 1, 105: ..

        # 深交所融券卖出标的
        sql4 = '''select InnerCode from MT_TargetSecurities where TargetFlag = 1 and SecuMarket = 90 and TargetCategory = 20;'''
        ret4 = juyuan.select_all(sql4)
        ret4 = [r.get("InnerCode") for r in ret4]
        # print(ret4)
        # print(len(ret4), len(set(ret4)))
        print(Counter(ret4))   # Counter({12243: 2, 16175: 2, 403: 1, 433: 1,  ..

        print(set(ret3) == set(ret4))

        # 查询聚源的最近更新时间
        sql5 = '''select max(UpdateTime) as max_dt from MT_TargetSecurities ; '''
        ret5 = juyuan.select_one(sql5).get("max_dt")
        print(ret5)    # 2020-04-20 09:04:01

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

    def _create_table(self):
        juyuan_sql = '''
        CREATE TABLE `mt_targetsecurities` (
          `ID` bigint(20) NOT NULL COMMENT 'ID',
          `SecuMarket` int(11) DEFAULT NULL COMMENT '证券市场',
          `InnerCode` int(11) NOT NULL COMMENT '证券内部编码',
          `InDate` datetime NOT NULL COMMENT '调入日期',
          `OutDate` datetime DEFAULT NULL COMMENT '调出日期',
          `TargetCategory` int(11) NOT NULL COMMENT '标的类别',
          `TargetFlag` int(11) DEFAULT NULL COMMENT '标的状态',
          `ChangeReasonDesc` varchar(2000) DEFAULT NULL COMMENT '变更原因描述',
          `UpdateTime` datetime NOT NULL COMMENT '更新时间',
          `JSID` bigint(20) NOT NULL COMMENT 'JSID',
          UNIQUE KEY `IX_MT_TargetSecurities_ID` (`ID`),
          UNIQUE KEY `IX_MT_TargetSecurities_JSID` (`JSID`),
          UNIQUE KEY `IX_MT_TargetSecurities` (`InnerCode`,`TargetCategory`,`InDate`,`OutDate`,`TargetFlag`)
        ) ENGINE=InnoDB DEFAULT CHARSET=gbk; 
        '''
        # TODO 注意不能像聚源一样将可能为 空 的 OutDate 设置为唯一索引
        # https://blog.csdn.net/xiaobao5214/article/details/100920837
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
          `SecuMarket` int(11) DEFAULT NULL COMMENT '证券市场',
          `InnerCode` int(11) NOT NULL COMMENT '证券内部编码',
          `InDate` datetime NOT NULL COMMENT '调入日期',
          `OutDate` datetime DEFAULT NULL COMMENT '调出日期',
          `TargetCategory` int(11) NOT NULL COMMENT '标的类别',
          `TargetFlag` int(11) DEFAULT NULL COMMENT '标的状态',
          `ChangeReasonDesc` varchar(2000) DEFAULT NULL COMMENT '变更原因描述',
          `UpdateTime` datetime NOT NULL COMMENT '数据源更新时间',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `IX_MT_TargetSecurities` (`SecuMarket`, `InnerCode`,`TargetCategory`,`InDate`,`TargetFlag`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='融资融券标的证券变更记录';
        '''.format(self.target_table_name)

        target = self._init_pool(self.product_cfg)
        target.insert(sql)
        target.dispose()
        logger.info("尝试建表")

        # 10-融资买入标的，20-融券卖出标的

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

    def parse_announcement(self):
        """从公告中提取更改信息 """
        # 公告链接地址: http://www.sse.com.cn/disclosure/magin/announcement/

        # 在聚源的最大更新时间之后的有：
        # (1) 4.23 的公告: http://www.sse.com.cn/disclosure/magin/announcement/ssereport/c/c_20200423_5052948.shtml
        # 内容: 在2020年4月24日将天津松江（600225） 调出融资融券标的证券名单
        inner_code = self.get_inner_code('600225')
        print(inner_code)  # 1346

        # (2) 4.28 的公告: http://www.sse.com.cn/disclosure/magin/announcement/ssereport/c/c_20200428_5067981.shtml
        # 内容: 在2020年4月29日将 博信股份（600083） 调出融资融券标的证券名单
        inner_code = self.get_inner_code("600083")
        print(inner_code)   # 1205

        # (3）4.29 的公告: http://www.sse.com.cn/disclosure/magin/announcement/ssereport/c/c_20200429_5075757.shtml
        # 内容: 于2020年4月30日将 交大昂立（600530）和宏图高科（600122）调出融资融券标的证券名单
        inner_code_1 = self.get_inner_code('600530')
        inner_code_2 = self.get_inner_code('600122')
        print(inner_code_1, inner_code_2)  # 1694 1250

        # (4) 4.30 的公告:http://www.sse.com.cn/disclosure/magin/announcement/ssereport/c/c_20200430_5085195.shtml
        # 内容: 于2020年5月6日将 美都能源（600175）、六国化工（600470）、飞乐音响（600651）、安信信托（600816）和宜华生活（600978）调出融资融券标的证券名单。
        in_co_1 = self.get_inner_code('600175')
        in_co_2 = self.get_inner_code('600470')
        in_co_3 = self.get_inner_code('600651')
        in_co_4 = self.get_inner_code('600816')
        in_co_5 = self.get_inner_code('600978')
        print(in_co_1, in_co_2, in_co_3, in_co_4, in_co_5)  # 1293 1612 1868 2051 2908

        pass

    def start(self):
        # self._create_table()
        # self.load_juyuan()

        self.show_juyuan_datas()

        # self.parse_announcement()

        # spider_list = self.get_spider_latest_list(83, 10)
        # print(spider_list)

        pass


if __name__ == "__main__":
    now = lambda: time.time()
    start_time = now()
    ShSync().start()
    logger.info(f"用时: {now() - start_time} 秒")    # (end)大概是 80s (dispose)大概是 425s
