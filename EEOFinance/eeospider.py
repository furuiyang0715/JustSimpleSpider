# 经济观察网



class EEOSpider(object):
    def __init__(self):
        # 起始首页链接
        self.index_url = 'http://www.eeo.com.cn/'
        self.topics = [
            'http://www.eeo.com.cn/shangyechanye/',  # 商业产业
            'http://www.eeo.com.cn/caijing/',  # 财经
            'http://www.eeo.com.cn/dichan/',  # 地产
            'http://www.eeo.com.cn/qiche/',  # 汽车
            'http://www.eeo.com.cn/tmt/',  # tmt
            'http://www.eeo.com.cn/pinglun/',  # 评论
            'http://www.eeo.com.cn/yanjiuyuan/',  # 研究院
        ]
        pass