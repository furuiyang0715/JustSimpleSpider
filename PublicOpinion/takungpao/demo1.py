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

fk = 'http://finance.takungpao.com/fk/'
body = re.get(fk).text
# print(body)
'''
<div class="wrap-l js-list fl_dib">
    <ul>
        <li class="mod_top_li clearfix">
            <div class="list-img fl_dib">
                <a href="http://finance.takungpao.com/fk/2017-08/3486877.html" target="_blank"><img src="http://images.takungpao.com/2017/0825/20170825030343655.jpg" /></a>
            </div>
            <div class="list-text fr_dib">
                <h1><a href="http://finance.takungpao.com/fk/2017-08/3486877.html" target="_blank">&quot;租赁&quot;披&quot;共享&quot;外衣站上风口 共享经济被&quot;玩坏&quot;</a></h1>
                <div class="cont">蜂拥进入共享经济领域的各类企业和个人很大部分是为了圈钱，或者通过收取押金获得大量资金，或者通过创造的共享经济故事来吸引投资。</div>
                <div class="date">2017-08-25</div>
            </div>
        </li>
'''
doc = html.fromstring(body)
news_list = doc.xpath('//div[@class="wrap-l js-list fl_dib"]/ul/li/div[@class="list-text fr_dib"]')
print(len(news_list))

for news in news_list:
    # print(news.text_content().split("\r\n"))
    title = news.xpath('./h1/a')[0].text_content()
    print(title)
    link = news.xpath('./h1/a/@href')[0]
    print(link)
    pub_date = news.xpath('./div[@class="date"]')[0].text_content()
    print(pub_date)

    pass



