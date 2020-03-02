from PublicOpinion.takungpao.hkstock_cjss import HKStock_CJSS


class HKStock_QQGS(HKStock_CJSS):

    def __init__(self):
        super(HKStock_QQGS, self).__init__()
        self.page = 10
        self.name = '全球股市'
        self.first_url = 'http://finance.takungpao.com/hkstock/qqgs/index.html'
        self.format_url = "http://finance.takungpao.com/hkstock/qqgs/index_{}.html"


if __name__ == "__main__":
    cjss = HKStock_QQGS()
    cjss.start()
