import logging
import time

from margin.base import MarginBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ShSync(MarginBase):
    """上交融资融券标的"""
    def __init__(self):
        self.juyuan_table_name = 'MT_TargetSecurities'
        self.target_table_name = 'MT_TargetSecurities'

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
        print(ret1)
        print(len(ret1))

        # 上交所融券卖出标的列表
        sql2 = '''select InnerCode from MT_TargetSecurities where TargetFlag = 1 and SecuMarket = 83 and TargetCategory = 20;'''
        ret2 = juyuan.select_all(sql2)
        ret2 = [r.get("InnerCode") for r in ret2]
        print(ret2)
        print(len(ret2))

        print(set(ret1) == set(ret2))

        # 深交所融资买入标的
        sql3 = '''select InnerCode from MT_TargetSecurities where TargetFlag = 1 and SecuMarket = 90 and TargetCategory = 10;'''
        ret3 = juyuan.select_all(sql3)
        ret3 = [r.get("InnerCode") for r in ret3]
        print(ret3)
        print(len(ret3))

        # 深交所融券卖出标的
        sql4 = '''select InnerCode from MT_TargetSecurities where TargetFlag = 1 and SecuMarket = 90 and TargetCategory = 20;'''
        ret4 = juyuan.select_all(sql4)
        ret4 = [r.get("InnerCode") for r in ret4]
        print(ret4)
        print(len(ret4))

        print(set(ret3) == set(ret4))

        # 查询聚源的最近更新时间
        sql5 = '''select max(UpdateTime) as max_dt from MT_TargetSecurities ; '''
        ret5 = juyuan.select_one(sql5).get("max_dt")
        print(ret5)    # 2020-04-20 09:04:01

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

    def start(self):
        # self._create_table()
        # self.load_juyuan()

        self.show_juyuan_datas()


if __name__ == "__main__":
    now = lambda: time.time()
    start_time = now()
    ShSync().start()
    logger.info(f"用时: {now() - start_time} 秒")    # (end)大概是 80s (dispose)大概是 425s
