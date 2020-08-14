import datetime
import re

import requests
from lxml import html

url = 'http://www.eeo.com.cn/2020/0814/399365.shtml'


resp = requests.get(url)

if resp and resp.status_code == 200:
    body = resp.text.encode("ISO-8859-1").decode("utf-8")
    doc = html.fromstring(body)
    try:
        article = doc.xpath(".//div[@class='xx_boxsing']")[0]
        article = article.text_content()
    except:
        article = ''

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

    print(author, "\n", pub_date, "\n", article)

    # print(article)

