from PublicOpinion.takungpao.hkstock_cjss import HKStock_CJSS


class HKStock_JGSD(HKStock_CJSS):

    def __init__(self):
        super(HKStock_JGSD, self).__init__()
        self.page = 9
        self.name = '机构视点'
        self.first_url = 'http://finance.takungpao.com/hkstock/jgsd/index.html'
        self.format_url = "http://finance.takungpao.com/hkstock/jgsd/index_{}.html"


if __name__ == "__main__":
    cjss = HKStock_JGSD()
    cjss.start()
