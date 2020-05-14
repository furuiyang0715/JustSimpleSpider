from takungpao import ZhongGuoJingJi


class HKStock(ZhongGuoJingJi):

    def __init__(self):
        super(HKStock, self).__init__()
        self.name = "港股"
        self.first_url = 'http://www.takungpao.com/finance/236135/index.html'
        self.format_url = 'http://www.takungpao.com/finance/236135/{}.html'


if __name__ == "__main__":
    hks = HKStock()
    hks.start()
