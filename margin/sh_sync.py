import logging

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
                         # 'UpdateTime', 'JSID',
                         ]
        select_str = ",".join(select_fields).rstrip(",")
        # print(select_str)

        juyuan = self._init_pool(self.juyuan_cfg)
        sql = '''select {} from {};'''.format(select_str, self.juyuan_table_name)
        ret = juyuan.select_all(sql)
        # print(len(ret))
        # print(ret[10])
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
          `UpdateTime` datetime NOT NULL COMMENT '更新时间',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `IX_MT_TargetSecurities` (`InnerCode`,`TargetCategory`,`InDate`,`OutDate`,`TargetFlag`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='融资融券标的证券变更记录';
        '''.format(self.target_table_name)

        target = self._init_pool(self.product_cfg)
        target.insert(sql)
        target.dispose()
        logger.info("尝试建表")

    def start(self):
        self._create_table()


if __name__ == "__main__":
    ShSync().start()