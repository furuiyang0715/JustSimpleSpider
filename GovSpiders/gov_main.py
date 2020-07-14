from GovSpiders.china_bank import ChinaBankShuJuJieDu, ChinaBankXinWenFaBu
from GovSpiders.gov_stats_sjjd import GovStatsShuJuJieDu
from GovSpiders.gov_stats_tjdt import GovStatsTongJiDongTai
from GovSpiders.gov_stats_xwfbh import GovStatsXinWenFaBuHui
from GovSpiders.gov_stats_zxfb import GovStatsZuiXinFaBu
from base import logger


class ChinaBankSchedule(object):
    class_lst = [
        ChinaBankShuJuJieDu,
        ChinaBankXinWenFaBu
    ]

    table_name = 'chinabank'
    dt_benchmark = 'pub_date'

    def ins_start(self, instance):
        instance.start()

    def start(self):
        """顺次运行"""
        for cls in self.class_lst:
            ins = cls()
            logger.info(f"中国银行 --> {ins.name}")
            ins.start()


class GovStatsSchedule(object):
    class_lst = [
        GovStatsShuJuJieDu,
        GovStatsTongJiDongTai,
        GovStatsXinWenFaBuHui,
        GovStatsZuiXinFaBu,
    ]

    table_name = 'gov_stats'
    dt_benchmark = 'pub_date'

    def start(self):
        """顺次运行"""
        for cls in self.class_lst:
            ins = cls()
            logger.info(f"中国银行 --> {ins.name}")
            ins.start()


if __name__ == "__main__":
    # ChinaBankSchedule().start()

    GovStatsSchedule().start()
