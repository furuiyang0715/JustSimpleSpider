from PublicOpinion.takungpao.hkstock_cjss import HKStock_CJSS


class HKStock_GJJJ(HKStock_CJSS):

    def __init__(self):
        super(HKStock_GJJJ, self).__init__()
        self.page = 5
        self.name = '国际聚焦'
        self.first_url = 'http://finance.takungpao.com/hkstock/gjjj/index.html'
        self.format_url = "http://finance.takungpao.com/hkstock/gjjj/index_{}.html"


if __name__ == "__main__":
    cjss = HKStock_GJJJ()
    cjss.start()