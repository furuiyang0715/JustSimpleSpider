from PublicOpinion.takungpao.zhongguojingji import ZhongGuoJingJi


class NewFinanceTrend(ZhongGuoJingJi):

    def __init__(self):
        super(NewFinanceTrend, self).__init__()
        self.name = '新经济浪潮'
        self.first_url = 'http://www.takungpao.com/finance/236160/index.html'
        self.format_url = 'http://www.takungpao.com/finance/236160/{}.html'
        self.page = 3


if __name__ == "__main__":
    busi = NewFinanceTrend()
    busi.start()
