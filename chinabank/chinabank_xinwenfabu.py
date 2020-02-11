from chinabank.china_bank_shujujiedu import ChinaBankShuJuJieDu
from chinabank.common.sqltools.mysql_pool import MqlPipeline


class ChinaBankXinWenFaBu(ChinaBankShuJuJieDu):
    def __init__(self):
        super(ChinaBankXinWenFaBu, self).__init__()
        self.name = '中国银行-新闻发布'
        self.table = "chinabank_xinwenfabu"
        self.url = "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/11040/index{}.html"
        self.pool = MqlPipeline(self.sql_client, self.db, self.table)


if __name__ == "__main__":
    demo = ChinaBankXinWenFaBu()
    demo._start()
