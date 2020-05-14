from takungpao import HKStock_CJSS


class HKStock_GSYW(HKStock_CJSS):

    def __init__(self):
        super(HKStock_GSYW, self).__init__()
        self.name = '公司要闻'
        self.first_url = 'http://finance.takungpao.com/hkstock/gsyw/index.html'
        self.format_url = "http://finance.takungpao.com/hkstock/gsyw/index_{}.html"


if __name__ == "__main__":
    cjss = HKStock_GSYW()
    cjss.start()
