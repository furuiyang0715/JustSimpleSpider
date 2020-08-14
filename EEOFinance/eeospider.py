import datetime
import re
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
        # print(self.topic_urls)

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'PHPSESSID=7avdv48orrl42d4s323eae4dn5; acw_tc=2760775215970417166888855e8f887a018cbf5f73aab22ec8d9ae03f7e2b4; SERVERID=adeed77a8e607bd6b1d16fea05016e81|1597041716|1597041716',
            'Host': 'www.eeo.com.cn',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
        }

    def get_topic(self, url):
        """获取栏目资讯"""
        resp = requests.get(url)
        if resp and resp.status_code == 200:
            text = resp.text.encode("ISO-8859-1").decode("utf-8")
            doc = html.fromstring(text)
            articles = doc.xpath(".//div[@class='list']/ul[@id='lyp_article']/li")
            items = []
            for article in articles:
                link = article.xpath("./a/@href")[0]   # 文章链接
                title = article.xpath(".//p")[0].text_content()    # 文章标题
                ret = self.get_detail(link)

                if not ret:
                    continue

                elif isinstance(ret, str):
                    item = {
                        'link': link,
                        'title': title,
                        'article': ret,
                    }

                else:   # isinstance(ret, tuple):
                    item = {
                        'link': link,
                        'title': title,
                        'author': ret[0],
                        'pub_date': ret[1],
                        'article': ret[2],
                    }
                items.append(item)
            return items
        return None

    def get_detail(self, url, is_api=False):
        resp = requests.get(url)
        if resp and resp.status_code == 200:
            body = resp.text.encode("ISO-8859-1").decode("utf-8")
            doc = html.fromstring(body)
            try:
                article = doc.xpath(".//div[@class='xx_boxsing']")[0]
                article = article.text_content()
            except:
                article = ''

            if is_api:
                return article
            else:
                try:
                    head_part = doc.xpath(".//div[@class='xd-b-b']")[0]
                    pub_info = head_part.xpath("./p")[0]
                    pub_info = pub_info.text_content()
                    pub_date = re.findall(r"\d{4}-\d{2}-\d{2}", pub_info)[0]  # 匹配出时间
                    pub_date = pub_date.strip()
                    pub_date = datetime.datetime.strptime(pub_date, "%Y-%m-%d")
                    author = re.findall(r'[\u4e00-\u9fa5]+', pub_info)[0]  # 匹配出作者
                except:
                    pub_date = ''
                    author = ''
                return author, pub_date, article
        return None

    def start(self):
        for url in self.topic_urls:
            print(url)
            ret = self.get_topic(url)
            for r in ret:
                print(r)

            print()
            print()
            print()
            print()

            sys.exit(0)


if __name__ == '__main__':
    eeo = EEOSpider()
    eeo.start()

    pass
