from GovSpiders.china_bank_shujujiedu import ChinaBankShuJuJieDu


class ChinaBankXinWenFaBu(ChinaBankShuJuJieDu):
    def __init__(self):
        super(ChinaBankXinWenFaBu, self).__init__()
        self.name = '中国银行-新闻发布'
        self.table = "chinabank"
        self.srart_url = "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/11040/index{}.html"


if __name__ == "__main__":
    demo = ChinaBankXinWenFaBu()
    demo._start(1)
    print(demo.error_list)
    print(demo.error_detail)
