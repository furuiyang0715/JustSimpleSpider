import datetime
import logging
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

        # # (1) http://www.szse.cn/disclosure/notice/general/t20200415_575996.html
        # # 本所于2020年4月16日起将 000727 调出融资融券标的证券名单
        # inner_code = self.get_inner_code('000727')
        # print(inner_code)    # 401
        # '''
        # mysql> select * from MT_TargetSecurities where InnerCode = '401';
        # +--------------+------------+-----------+---------------------+---------------------+----------------+------------+------------------+---------------------+--------------+
        # | ID           | SecuMarket | InnerCode | InDate              | OutDate             | TargetCategory | TargetFlag | ChangeReasonDesc | UpdateTime          | JSID         |
        # +--------------+------------+-----------+---------------------+---------------------+----------------+------------+------------------+---------------------+--------------+
        # | 619614010487 |         90 |       401 | 2019-08-19 00:00:00 | 2020-04-16 00:00:00 |             10 |          0 | NULL             | 2020-04-16 10:24:11 | 640347851196 |
        # | 619614010510 |         90 |       401 | 2019-08-19 00:00:00 | 2020-04-16 00:00:00 |             20 |          0 | NULL             | 2020-04-16 10:24:11 | 640347851197 |
        # +--------------+------------+-----------+---------------------+---------------------+----------------+------------+------------------+---------------------+--------------+
        # 2 rows in set (0.04 sec)
        # '''

 #        # (2） http://www.szse.cn/disclosure/notice/general/t20200428_576534.html
 #        # 本所于2020年4月29日起将 000536 调出融资融券标的证券名单
 #        target = self._init_pool(self.product_cfg)
 #        inner_code = self.get_inner_code("000536")   # 220
 #        '''
 #        mysql> select * from MT_TargetSecurities where InnerCode = '220';
 #        +--------------+------------+-----------+---------------------+---------+----------------+------------+------------------+---------------------+--------------+
 #        | ID           | SecuMarket | InnerCode | InDate              | OutDate | TargetCategory | TargetFlag | ChangeReasonDesc | UpdateTime          | JSID         |
 #        +--------------+------------+-----------+---------------------+---------+----------------+------------+------------------+---------------------+--------------+
 #        | 624019264531 |         90 |       220 | 2014-09-22 00:00:00 | NULL    |             10 |          1 | NULL             | 2019-10-10 10:41:01 | 624019264532 |
 #        | 624019264533 |         90 |       220 | 2014-09-22 00:00:00 | NULL    |             20 |          1 | NULL             | 2019-10-10 10:41:01 | 624019264534 |
 #        +--------------+------------+-----------+---------------------+---------+----------------+------------+------------------+---------------------+--------------+
 #        2 rows in set (0.01 sec)
 #        '''
 #        dt = datetime.datetime(2020, 4, 29)
 #        sql = '''update {} set OutDate = '{}', TargetFlag = 2 where SecuMarket = 90 and InnerCode = {}\
 # and TargetCategory in (10, 20) and TargetFlag = 1; '''.format(self.target_table_name, dt, inner_code)
 #        ret = target.update(sql)
 #        '''
 #        mysql> select * from MT_TargetSecurities where InnerCode = '220';
 #        +------+------------+-----------+---------------------+---------------------+----------------+------------+------------------+---------------------+---------------------+---------------------+
 #        | id   | SecuMarket | InnerCode | InDate              | OutDate             | TargetCategory | TargetFlag | ChangeReasonDesc | UpdateTime          | CREATETIMEJZ        | UPDATETIMEJZ        |
 #        +------+------------+-----------+---------------------+---------------------+----------------+------------+------------------+---------------------+---------------------+---------------------+
 #        | 6971 |         90 |       220 | 2014-09-22 00:00:00 | 2020-04-29 00:00:00 |             10 |          2 | NULL             | 2019-10-10 10:41:01 | 2020-05-07 14:42:48 | 2020-05-08 17:28:27 |
 #        | 6973 |         90 |       220 | 2014-09-22 00:00:00 | 2020-04-29 00:00:00 |             20 |          2 | NULL             | 2019-10-10 10:41:01 | 2020-05-07 14:42:48 | 2020-05-08 17:28:27 |
 #        +------+------------+-----------+---------------------+---------------------+----------------+------------+------------------+---------------------+---------------------+---------------------+
 #        2 rows in set (0.01 sec)
 #        '''
 #        try:
 #            target.dispose()
 #        except:
 #            pass

        # # (3) http://www.szse.cn/disclosure/notice/general/t20200429_576572.html
        # # 本所于2020年4月30日起将002176股票调出融资融券标的证券名单
        # target = self._init_pool(self.product_cfg)
        # dt = datetime.datetime(2020, 4, 30)
        # inner_code = self.get_inner_code('002176')
        # # print(inner_code)   # 6139
        #
        # sql = '''update {} set OutDate = '{}', TargetFlag = 2 where SecuMarket = 90 and InnerCode = {}\
        # and TargetCategory in (10, 20) and TargetFlag = 1; '''.format(self.target_table_name, dt, inner_code)
        # ret = target.update(sql)
        # print(ret)
        # target.dispose()

        #








        pass

    def start(self):
        # self._create_table()

        self.parse_announcemen_byhuman()

        pass


if __name__ == "__main__":
    now = lambda: time.time()
    start_time = now()
    SzGener().start()
    logger.info(f"用时: {now() - start_time} 秒")    # (end)大概是 80s (dispose)大概是 425s
