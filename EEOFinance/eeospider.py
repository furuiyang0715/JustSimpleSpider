import sys

import requests
from lxml import html


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

    def get_topic(self, url):
        """获取栏目资讯"""
        '''
    <li>
        <a href="http://www.eeo.com.cn/2020/0813/398971.shtml" target="_blank">
        <img width=311px height=159px src="http://upload.eeo.com.cn/2020/0813/thumb_311_159_1597304928597.png" />
            <span class="cls"></span>
        </a> 
        <div>
            <span data-cid="398971"><a href="http://www.eeo.com.cn/2020/0813/398971.shtml" target="_blank">“深圳东·新一代‘智’造中心”华夏顺泽惠阳信息科技园正在出发</a></span>
            <p>华夏顺泽惠阳信息科技园毗邻深圳东的惠州市惠阳区，正在成为粤港澳大湾区信息科技产业版图上快速崛起的“新贵”。</p>
            <a href="http://www.eeo.com.cn/eeo/shangyechanye/dashi/">大事</a>							
        </div>
    </li>
        '''
        resp = requests.get(url)
        if resp and resp.status_code == 200:
            text = resp.text.encode("ISO-8859-1").decode("utf-8")
            # print(text)
            doc = html.fromstring(text)
            articles = doc.xpath(".//div[@class='list']/ul[@id='lyp_article']/li")
            for article in articles:
                # print(article)
                link = article.xpath("./a/@href")[0]   # 文章链接
                title = article.xpath(".//p")[0].text_content()    # 文章标题
                # print(title)
                # print(link)

    def start(self):
        for url in self.topic_urls:
            # print(url)
            self.get_topic(url)


            sys.exit(0)


if __name__ == '__main__':
    eeo = EEOSpider()
    eeo.start()

    pass
