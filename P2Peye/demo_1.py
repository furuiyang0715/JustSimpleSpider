import requests
from lxml import html

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
}


def get_index_page():
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






get_index_page()
