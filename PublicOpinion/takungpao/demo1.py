import pprint

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

travel = 'http://finance.takungpao.com/travel/'
body = re.get(travel).text
# print(body)
doc = html.fromstring(body)
news_list = doc.xpath('//div[@class="txtImgListeach current"]')
print(len(news_list))

for news in news_list:
    link = news.xpath("./h3/a/@href")[0]
    print(link)
    title = news.xpath("./h3/a")[0].text_content()
    print(title)
    pub_date = news.xpath(".//span[@class='time']")[0].text_content()
    print(pub_date)




