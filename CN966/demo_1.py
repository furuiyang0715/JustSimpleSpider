import datetime
import re

import requests
from lxml import html

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    'Cookie': 'cowboy_website=2a1644a5-0b40-4d46-93ca-367c54e39220; cowboy_visit_time=1595899251676; Hm_lvt_94656c824ef4eacf1a61cd662f7a7f17=1595899253; __utmc=236883550; __utmz=236883550.1595899253.1.1.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; cowboy_login=C3AD5319C3B607C2840F46C286C3AEC2B9C393C2AD3D3060C2896512423AC3B7C3B1596E2B47C282C3A21145C28C3E41C395C393C390C2A7C38B; cowboy_login_imply=C3AD5319C3B607C2840F46C286C3AEC2B9C393C2AD3D3060C2896512423AC3B7C3B1596E2B47C282C3A21145C28C3E41C395C393C390C2A7C38B; cowboy_nick_name=e882a1e58f8b343838393937; cowboy_user_name=nz_d09e0490; cowboy_latest_login_time=1595899414; Hm_lvt_11beb42de0d3859b0af4fd1b6f3b45cf=1595899267,1595899423,1595899565; Hm_lpvt_94656c824ef4eacf1a61cd662f7a7f17=1595902758; Hm_lpvt_11beb42de0d3859b0af4fd1b6f3b45cf=1595902758; __utma=236883550.1639834052.1595899253.1595899253.1595902758.2; __utmt=1; __utmb=236883550.2.9.1595902758; JSESSIONID=DBE042153E24D84C8E659A9DFDB824ED',
}


def get_list(url):
    # url = 'http://pinglun.9666.cn/zaowanping/'    # 早晚评
    resp = requests.get(url, headers=headers)
    # print(resp)
    if resp and resp.status_code == 200:
        body = resp.text
        # print(body)
        # print("震荡期行情略显低迷 关注主流品种能否强势" in body)
        doc = html.fromstring(body)
        news_list = doc.xpath(".//div[@id='hotspot_list_box']")
        # print(len(news_list))
        if news_list:
            news_list = news_list[0]
            boxs1 = news_list.xpath(".//div[@class='channel  clearfix list-box']")
            boxs2 = news_list.xpath(".//div[@class='channel clearfix list-box']")
            boxs1.extend(boxs2)
            # print(len(boxs1))
            for box in boxs1:
                info = box.xpath(".//div[@class='channel_one']/span[@class='f24 fb']/a")[0]
                link = info.xpath("./@href")[0]
                title = info.text_content()
                pub_str = box.xpath(".//p[@class='list-info gray01']")[0]
                pub_str = pub_str.text_content().strip()
                pub_date = re.findall("\d{2}-\d{2} \d{2}:\d{2}", pub_str)[0]
                pub_date = str(datetime.datetime.now().year) + "-" + pub_date
                print(link)
                print(title)
                print(pub_date)
                print()


# format_url = 'http://pinglun.9666.cn/zaowanping/?pager.offset=15&pageNo={}&pageSize=15'
#
# for page_num in range(2, 10):
#     print(page_num)
#     url = format_url.format(page_num)
#     get_list(url)


def get_detail(url):
    resp = requests.get(url, headers=headers)
    if resp and resp.status_code == 200:
        body = resp.text
        # print(body)
        # print("而且可乘机高抛一点，" in body)
        doc = html.fromstring(body)
        article = doc.xpath("//div[@class='blog-article']")[0]
        print(article.text_content())


get_detail("http://pinglun.9666.cn/2540296.html")
