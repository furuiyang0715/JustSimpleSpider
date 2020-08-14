class EEOSpider(object):
    """经济观察网"""
    def __init__(self):
        # 起始首页链接
        self.index_url = 'http://www.eeo.com.cn/'
        # 需要爬取的分逻辑
        self.topic_words = ['shangyechanye', 'caijing', 'dichan', 'qiche', 'tmt', 'pinglun', 'yanjiuyuan']
        self.topic_format_url = 'http://www.eeo.com.cn/{}/'
        self.topic_urls = [self.topic_format_url.format(topic) for topic in self.topic_words]
        print(self.topic_urls)

        # self.topics = [
        #     'http://www.eeo.com.cn/shangyechanye/',  # 商业产业
        #     'http://www.eeo.com.cn/caijing/',  # 财经
        #     'http://www.eeo.com.cn/dichan/',  # 地产
        #     'http://www.eeo.com.cn/qiche/',  # 汽车
        #     'http://www.eeo.com.cn/tmt/',  # tmt
        #     'http://www.eeo.com.cn/pinglun/',  # 评论
        #     'http://www.eeo.com.cn/yanjiuyuan/',  # 研究院
        # ]


if __name__ == '__main__':
    eeo = EEOSpider()

    pass