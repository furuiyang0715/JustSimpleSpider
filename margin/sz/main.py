import datetime
import logging
import sys
import time
from margin.base import MarginBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SzGener(MarginBase):
    def __init__(self):
        self.juyuan_table_name = 'MT_TargetSecurities'
        self.target_table_name = 'MT_TargetSecurities'
        # 爬虫库
        self.spider_table_name = 'targetsecurities'
        self.inner_code_map = self.get_inner_code_map()

        # 深交所的公告页
        self.announcemen_web = 'http://www.szse.cn/disclosure/margin/business/index.html'
        # 深交所的公告接口  TODO
        self.announcemen_web_api = 'http://www.szse.cn/api/search/content?random=0.5530111979175076'
        '''
        post 请求 
        接口数据： 
        keyword: 融资融券
        time: 0
        range: title
        channelCode[]: business_news
        currentPage: 1
        pageSize: 20
        '''

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

    def _create_table(self):
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

    def parse_announcemen_byhuman(self):
        """从公告中提取更改信息 """
        target = self._init_pool(self.product_cfg)

        # # (1) http://www.szse.cn/disclosure/notice/general/t20200415_575996.html
        # # 本所于2020年4月16日起将 南京华东电子信息科技股份有限公司股票（证券代码：000727）  调出融资融券标的证券名单
        # inner_code = self.get_inner_code('000727')
        # print(inner_code)    # 401

 #        # (2） http://www.szse.cn/disclosure/notice/general/t20200428_576534.html
 #        # 本所于2020年4月29日起将 华映科技（集团）股份有限公司股票（证券代码：000536）  调出融资融券标的证券名单
 #        inner_code = self.get_inner_code("000536")   # 220
 #        dt = datetime.datetime(2020, 4, 29)
 #        sql = '''update {} set OutDate = '{}', TargetFlag = 2 where SecuMarket = 90 and InnerCode = {}\
 # and TargetCategory in (10, 20) and TargetFlag = 1; '''.format(self.target_table_name, dt, inner_code)
 #        ret = target.update(sql)

        # (3) http://www.szse.cn/disclosure/notice/general/t20200429_576571.html
        # 本所于2020年4月30日起将 苏州胜利精密制造科技股份有限公司股票（证券代码：002426） 调出融资融券标的证券名单。
        # inner_code = self.get_inner_code('002426')
        # # print(inner_code)   # 10476
        # dt = datetime.datetime(2020, 4, 30)
        # sql = '''update {} set OutDate = '{}', TargetFlag = 2 where SecuMarket = 90 and InnerCode = {}\
        # and TargetCategory in (10, 20) and TargetFlag = 1; '''.format(self.target_table_name, dt, inner_code)
        # ret = target.update(sql)
        # print(ret)

        # (4) http://www.szse.cn/disclosure/notice/general/t20200429_576572.html
        # 本所于2020年4月30日起将  江西特种电机股份有限公司股票（证券代码：002176） 调出融资融券标的证券名单
        # dt = datetime.datetime(2020, 4, 30)
        # inner_code = self.get_inner_code('002176')
        # # print(inner_code)   # 6139
        # sql = '''update {} set OutDate = '{}', TargetFlag = 2 where SecuMarket = 90 and InnerCode = {}\
        # and TargetCategory in (10, 20) and TargetFlag = 1; '''.format(self.target_table_name, dt, inner_code)
        # ret = target.update(sql)
        # print(ret)

        # # (5) http://www.szse.cn/disclosure/notice/general/t20200430_576649.html
        # # 本所于2020年5月6日起将  深圳市奋达科技股份有限公司股票（证券代码：002681）  调出融资融券标的证券名单。
        # dt = datetime.datetime(2020, 5, 6)
        # inner_code = self.get_inner_code('002681')
        # # print(inner_code)   # 16668
        # sql = '''update {} set OutDate = '{}', TargetFlag = 2 where SecuMarket = 90 and InnerCode = {}\
        # and TargetCategory in (10, 20) and TargetFlag = 1; '''.format(self.target_table_name, dt, inner_code)
        # ret = target.update(sql)
        # print(ret)

        # (6)

        target.dispose()

    def start(self):
        # self._create_table()

        self.parse_announcemen_byhuman()

        pass


if __name__ == "__main__":
    now = lambda: time.time()
    start_time = now()
    SzGener().start()
    logger.info(f"用时: {now() - start_time} 秒")    # (end)大概是 80s (dispose)大概是 425s
