import requests
from lxml import html

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
}


def get_index_page():
    """从首页获取信息"""
    url = "https://news.p2peye.com/"
    # list_url = 'https://news.p2peye.com/xwzx/{}.html'.format(page)
    resp = requests.get(url, headers=headers)
    print(resp)
    if resp and resp.status_code == 200:
        page = resp.text
        # print(page)
        # print('新闻资讯' in page)
        # print('专栏文章' in page)
        # print('专题报道' in page)
        # print('天眼财经' in page)
        doc = html.fromstring(page)
        # 新闻资讯
        topics = doc.xpath(".//div[@class='news-wrap mod-news']")
        for topic in topics:
            news_list = topic.xpath(".//ul[@class='mod-list clearfix']")
            if news_list:
                for news_part in news_list:
                    # 图片新闻稍晚出现在列表新闻中 不必专门提取
                    # img_news = news_part.xpath(".//li[@class='img']")
                    # if img_news:
                    #     item = {}
                    #     img_news = img_news[0]
                    #     info = img_news.xpath("./a")[0]
                    #     # https://news.p2peye.com/article-563957-1.html
                    #     url = "https:" + info.xpath("./@href")[0]
                    #     title = info.xpath("./@title")[0]
                    #     item['link'] = url
                    #     item['title'] = title
                    #     print(item)
                    normal_news = news_part.xpath(".//li[contains(@class, 'list clearfix')]")
                    for one in normal_news:
                        item = {}
                        url = one.xpath(".//a/@href")[0]
                        title = one.xpath(".//a/@title")[0]
                        pub_date = one.xpath(".//span[@class='time']")[0].text_content()
                        item['link'] = "https:" + url
                        item['title'] = title
                        item['pub_date'] = pub_date
                        print(item)

            print()
            print()


def get_t1_list():
    """从新闻资讯页获取文章"""
    url = 'https://news.p2peye.com/xwzx/2.html'
    resp = requests.get(url, headers=headers)
    if resp and resp.status_code == 200:
        body = resp.text
        doc = html.fromstring(body)
        news_list = doc.xpath(".//div[@id='listbox92']")
        if news_list:
            news_list = news_list[0]
            news = news_list.xpath(".//div[@class='mod-leftfixed mod-news clearfix']")
            for part in news:
                item = dict()
                hd = part.xpath(".//div[@class='hd']/a")[0]
                link = hd.xpath("./@href")[0].lstrip("//")
                title = hd.xpath("./@title")[0]
                pub_date = part.xpath(".//div[@class='fd-left']/span")[-1].text_content()
                item['link'] = link
                item['title'] = title
                item['pub_date'] = pub_date
                print(item)
                print()


def get_t2_list():
    # 从专栏文章获取
    url = 'https://news.p2peye.com/wdzl/2.html'
    resp = requests.get(url, headers=headers)
    if resp and resp.status_code == 200:
        body = resp.text
        doc = html.fromstring(body)
        news_list = doc.xpath(".//div[@id='listbox26']")
        if news_list:
            news_list = news_list[0]
            news = news_list.xpath(".//div[@class='mod-leftfixed mod-news clearfix']")
            for part in news:
                item = dict()
                hd = part.xpath(".//div[@class='hd']/a")[0]
                link = hd.xpath("./@href")[0].lstrip("//")
                title = hd.xpath("./@title")[0]
                pub_date = part.xpath(".//div[@class='fd-left']/span")[-1].text_content()
                item['link'] = link
                item['title'] = title
                item['pub_date'] = pub_date
                print(item)
                print()


def get_t3_list():
    # 从天眼财经获取文章
    items = []
    url = 'https://news.p2peye.com/tycj/2.html'
    resp = requests.get(url, headers=headers)
    if resp and resp.status_code == 200:
        body = resp.text
        doc = html.fromstring(body)
        news_list = doc.xpath(".//div[@id='listbox75']")
        if news_list:
            news_list = news_list[0]
            news = news_list.xpath(".//div[@class='mod-leftfixed mod-news clearfix']")
            for part in news:
                item = dict()
                hd = part.xpath(".//div[@class='hd']/a")[0]
                link = hd.xpath("./@href")[0].lstrip("//")
                title = hd.xpath("./@title")[0]
                pub_date = part.xpath(".//div[@class='fd-left']/span")[-1].text_content()
                item['link'] = link
                item['title'] = title
                item['pub_date'] = pub_date
                print(item)
                print()


# get_index_page()
get_t1_list()
# get_t2_list()
# get_t3_list()
