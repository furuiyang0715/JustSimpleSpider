### 证券时报
import pprint

import requests as req
from gne import GeneralNewsExtractor
from lxml import html

extractor = GeneralNewsExtractor()
url = "http://news.stcn.com/"


def demo1():
    body = req.get(url).text
    print(body)


def demo2():
    body = req.get(url).text
    doc = html.fromstring(body)
    # first = doc.xpath("//dl[@class='hotNews']")[0]
    # # print(first)
    # # print(first.text_content())
    # title = first.xpath("//dt/a/@title")[0]
    # link = first.xpath("//dt/a/@href")[0]
    # pub_date = first.xpath("//dd[@class='sj']")[0].text_content()
    # pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
    # print(title)
    # print(link)
    # print(pub_date)

    columns = doc.xpath("//ul[@class='news_list']/li")
    # num = 0
    for column in columns:
        # num += 1
        # print(column.tag)
        title = column.xpath("./p[@class='tit']/a/@title")[0]
        link = column.xpath("./p[@class='tit']/a/@href")[0]
        pub_date = column.xpath("./p[@class='sj']")[0].text_content()
        pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
        print(title, link, pub_date)

    # print(num)


def demo3():
    # url = "http://kuaixun.stcn.com/2020/0220/15651349.shtml"
    url = "http://kuaixun.stcn.com/2020/0220/15651497.shtml"
    body = req.get(url).text
    doc = html.fromstring(body)
    nodes = doc.xpath("//div[@class='txt_con']/p")

    contents = []
    for node in nodes:
        contents.append(node.text_content())
    print(pprint.pformat(contents))
    article = "".join(contents)
    # print(article)
    return article



# demo1()
demo2()
# demo3()