import datetime
import pprint
import sys

import requests as re
from lxml import html


def parse_next():

    pass


def parse_list(body):
    items = []
    doc = html.fromstring(body)
    news_list = doc.xpath("//div[@class='m_txt_news']/ul/li")
    # print(news_list)
    # print(len(news_list))
    for news in news_list:
        item = {}
        title = news.xpath("./a[@class='a_title']")
        if not title:
            title = news.xpath("./a[@class='a_title txt_blod']")
        title = title[0].text_content()
        # print(title)
        item['title'] = title
        pub_date = news.xpath("./a[@class='a_time txt_blod']")
        if not pub_date:
            pub_date = news.xpath("./a[@class='a_time']")

        link = pub_date[0].xpath("./@href")[0]
        # print(link)
        item['link'] = link

        pub_date = pub_date[0].text_content()
        # print(pub_date)
        item['pub_date'] = pub_date
        items.append(item)
    return items


# url = 'http://finance.takungpao.com/hkstock/cjss/'
# url = 'http://finance.takungpao.com/hkstock/cjss/index_4.html'
# body = re.get(url).text
# items = parse_list(body)
# print(pprint.pformat(items))
# print(len(items))

# zhongguojingji = 'http://www.takungpao.com/finance/236132/index.html'
zhongguojingji = 'http://www.takungpao.com/finance/236132/2.html'
# Economic_observer 经济观察家
ob = "http://www.takungpao.com/finance/236134/index.html"
body = re.get(ob).text
# print(body)
doc = html.fromstring(body)
news_list = doc.xpath('//div[@class="sublist_mobile"]/dl[@class="item"]')
print(len(news_list))

# sys.exit(0)

for news in news_list:
    link = news.xpath('./dd[@class="intro"]/a/@href')[0]
    print(link)

    title = news.xpath("./dd/a/@title")
    print(title[0])

    pub_date = news.xpath("./dd[@class='date']/text()")[0]
    # # 发布时间的几种处理
    print(">>> ", pub_date)
    current_dt = datetime.datetime.now()
    yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    after_yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    if "小时前" in pub_date:  # eg. 20小时前
        hours = int(pub_date.replace('小时前', ''))
        pub_date = (current_dt - datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    elif "昨天" in pub_date:  # eg. 昨天04:24
        pub_date = pub_date.replace('昨天', '')
        pub_date = " ".join([yesterday_dt_str, pub_date])
    elif '前天' in pub_date:   # eg. 前天11:33
        pub_date = pub_date.replace("前天", '')
        pub_date = " ".join([after_yesterday_dt_str, pub_date])
    else:    # eg. 02-29 04:24
        pub_date = str(current_dt.year) + '-' + pub_date
    print(pub_date)
    print()
