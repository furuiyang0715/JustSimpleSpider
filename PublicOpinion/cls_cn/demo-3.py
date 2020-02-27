import json
import pprint
import re

import requests as req

main_url = 'https://www.cls.cn/reference/1'

ret = req.get(main_url)

# print(ret.text)

page = ret.text

# json_data = re.findall(r'jQuery\d{21}_\d{13}\((\{.*?\})\)', page)[0]
json_data = re.findall(r'__NEXT_DATA__ = (\{.*\})', page)[0]
# print(json_data)
py_data = json.loads(json_data)
# print(py_data)

# print(pprint.pformat(py_data))  # 'initialState' 'reference' 'morningNewsList':

news_list = py_data.get('props', {}).get('initialState', {}).get('reference', {}).get('morningNewsList')
# print(news_list)

items = []

for news in news_list:
    item = {}
    # print(news)

    # 判断是否是当前文章
    current = news.get("morningNewsContent")
    if current:
        # print(pprint.pformat(current))
        pub_date = news.get('morningNewsContent', {}).get("ctime")
        title = news.get('morningNewsContent', {}).get("title")
        article = news.get('morningNewsContent', {}).get("content")
        # print(pub_date)
        # print(title)
        # print(article)
        aid = news.get('id')
        link = 'https://api3.cls.cn/share/article/{}?os=web&sv=6.8.0&app=CailianpressWeb'.format(aid)
        # print(link)
        item['title'] = title
        item['pub_date'] = pub_date
        item['link'] = link
        item['article'] = article
    else:
        print(pprint.pformat(news))
        pub_date = news.get("ctime")
        title = news.get("title")
        aid = news.get('id')
        link = 'https://api3.cls.cn/share/article/{}?os=web&sv=6.8.0&app=CailianpressWeb'.format(aid)
        item['title'] = title
        item['pub_date'] = pub_date
        item['link'] = link
        # item['article'] = article

    items.append(item)


def paese_app_detail(link):
    page = req.get(link).text
    print(page)

    pass


for item in items:
    print(item)


