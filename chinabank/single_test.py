# 对于出错的页面进行单独的脚本测试
import pprint
import sys

from lxml import html
from selenium import webdriver


# 105, 109, 112
url = "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/11040/index112.html"

browser = webdriver.Chrome()
browser.implicitly_wait(30)
browser.get(url)
list_page = browser.page_source


def parse_list_page(list_page):
    """
    解析列表页
    :param list_page:
    :return:
    """
    doc = html.fromstring(list_page)
    # opentype="page"
    news_area = doc.xpath("//div[@opentype='page']")[0]
    # print("------> ", news_area)

    # sys.exit(0)

    news_title_parts = news_area.xpath(".//font[@class='newslist_style']")
    # print(news_title_parts)

    # sys.exit(0)
    items = []

    # sys.exit(0)

    for news_title_part in news_title_parts:
        item = {}
        # news_date_part = news_title_part.xpath("./following-sibling::span[@class='hui12']")
        # print(news_date_part)
        try:
            news_date_part = news_title_part.xpath("./following-sibling::span[@class='hui12']")[0].text_content()
        except:
            news_date_part = news_title_part.xpath("./following-sibling::a/span[@class='hui12']")[0].text_content()

        item["pubdate"] = news_date_part  # 发布时间

        news_title = news_title_part.xpath("./a")[0].text_content()
        # print(news_title)
        item["article_title"] = news_title  # 文章标题

        news_link = news_title_part.xpath("./a/@href")[0]
        news_link = "http://www.pbc.gov.cn" + news_link
        item["article_link"] = news_link  # 文章详情页链接
        # print(news_link)
        items.append(item)

    return items


ret = parse_list_page(list_page)

print(pprint.pformat(ret))

browser.close()