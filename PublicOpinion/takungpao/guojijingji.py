from PublicOpinion.takungpao.zhongguojingji import ZhongGuoJingJi


class GuoJiJingJi(ZhongGuoJingJi):

    def __init__(self):
        super(GuoJiJingJi, self).__init__()
        self.name = "国际经济"
        self.first_url = 'http://www.takungpao.com/finance/236133/index.html'
        self.format_url = 'http://www.takungpao.com/finance/236133/{}.html'


if __name__ == "__main__":
    gj = GuoJiJingJi()
    gj.start()
