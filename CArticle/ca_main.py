import random

from CArticle.ca_spider import CArticleSpiser
from base import SpiderBase, logger


class CaSchedule(SpiderBase):
    table_name = "eastmoney_carticle"
    dt_benchmark = 'pub_date'

    def __init__(self):
        super(CaSchedule, self).__init__()
        self.keys = list(self.dc_info().values())
        random.shuffle(self.keys)

    def dc_info(self):
        self._dc_init()
        sql = '''select SecuCode, ChiNameAbbr from const_secumain where SecuCode \
            in (select distinct SecuCode from const_secumain);'''
        datas = self.dc_client.select_all(sql)
        dc_info = {r['SecuCode']: r['ChiNameAbbr'] for r in datas}
        return dc_info

    def run(self, key):
        CArticleSpiser(key=key).start()

    def _create_table(self):
        self._spider_init()
        sql = '''
           CREATE TABLE IF NOT EXISTS `{}` (
             `id` int(11) NOT NULL AUTO_INCREMENT,
             `pub_date` datetime NOT NULL COMMENT '发布时间',
             `code` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '股票代码',
             `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
             `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
             `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
             `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
             `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
             PRIMARY KEY (`id`),
             UNIQUE KEY `link` (`link`),
             KEY `pub_date` (`pub_date`),
             KEY `update_time` (`UPDATETIMEJZ`)
           ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='东财-财富号文章'; 
           '''.format(self.table_name)
        self.spider_client.insert(sql)
        self.spider_client.end()

    def start(self):
        self._create_table()
        for key in self.keys:
            logger.info("当前的主题是: {}".format(key))
            self.run(key)


def task():
    CaSchedule().run()


if __name__ == '__main__':
    task()
