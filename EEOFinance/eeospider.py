class EEOSpider(object):
    """经济观察网"""
    def __init__(self):
        # 起始首页链接
        self.index_url = 'http://www.eeo.com.cn/'
        # 需要爬取的分逻辑
        self.topic_words = [
            'shangyechanye',  # 商业产业
            'caijing',        # 财经
            'dichan',         # 地产
            'qiche',          # 汽车
            'tmt',            # tmt
            'pinglun',        # 评论
            'yanjiuyuan',     # 研究院
        ]
        self.topic_format_url = 'http://www.eeo.com.cn/{}/'
        self.topic_urls = [self.topic_format_url.format(topic) for topic in self.topic_words]
        print(self.topic_urls)


if __name__ == '__main__':
    eeo = EEOSpider()

    pass
