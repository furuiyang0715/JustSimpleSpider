from takungpao import HKStock_CJSS


class HKStock_JJYZ(HKStock_CJSS):

    def __init__(self):
        super(HKStock_JJYZ, self).__init__()
        self.page = 3
        self.name = '经济一周'
        self.first_url = 'http://finance.takungpao.com/hkstock/jjyz/index.html'
        self.format_url = "http://finance.takungpao.com/hkstock/jjyz/index_{}.html"


if __name__ == "__main__":
    cjss = HKStock_JJYZ()
    cjss.start()
