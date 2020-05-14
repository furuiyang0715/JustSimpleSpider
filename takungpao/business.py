from takungpao import ZhongGuoJingJi


class Business(ZhongGuoJingJi):

    def __init__(self):
        super(Business, self).__init__()
        self.name = '商业'
        self.first_url = 'http://www.takungpao.com/finance/236137/index.html'
        self.format_url = 'http://www.takungpao.com/finance/236137/{}.html'


if __name__ == "__main__":
    busi = Business()
    busi.start()
