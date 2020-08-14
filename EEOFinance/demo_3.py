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
    print(article)

