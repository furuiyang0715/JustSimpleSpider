from takungpao import ZhongGuoJingJi


class DiChan(ZhongGuoJingJi):

    def __init__(self):
        super(DiChan, self).__init__()
        self.name = '地产'
        self.first_url = 'http://www.takungpao.com/finance/236136/index.html'
        self.format_url = 'http://www.takungpao.com/finance/236136/{}.html'


if __name__ == "__main__":
    dc = DiChan()
    dc.start()
