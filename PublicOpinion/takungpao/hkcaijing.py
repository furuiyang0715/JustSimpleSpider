from PublicOpinion.takungpao.zhongguojingji import ZhongGuoJingJi


class HKCaiJing(ZhongGuoJingJi):

    def __init__(self):
        super(HKCaiJing, self).__init__()
        self.name = '香港财经'
        self.first_url = 'http://www.takungpao.com/finance/236131/index.html'
        self.format_url = 'http://www.takungpao.com/finance/236131/{}.html'


if __name__ == "__main__":
    hkc = HKCaiJing()
    hkc.start()
