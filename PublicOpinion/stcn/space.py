import datetime

import requests
from gne import GeneralNewsExtractor
from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base


class STCN_Column(STCN_Base):
    # 专栏
    def __init__(self):
        super(STCN_Column, self).__init__()
        self.list_url = "http://space.stcn.com"
        self.extractor = GeneralNewsExtractor()
        self.name = '专栏'

    def _get(self, url):
        resp = requests.get(url)
        if resp.status_code == 200:
            body = resp.text.encode("ISO-8859-1").decode("utf-8")
            return body

    def _parse_detail(self, body):
        try:
            result = self.extractor.extract(body)
            content = result.get("content")
        except:
            return None
        else:
            return content

    def _parse_list_body(self, body):
        # print(body)
        doc = html.fromstring(body)
        items = []
        # 列表文章
        columns = doc.xpath('//div[@id="news_list2"]/dl')
        # print(columns)
        num = 0
        for column in columns:
            num += 1
            # print(column.tag)
            title = column.xpath('./dd[@class="mtit"]/a/@title')[0]
            link = column.xpath('./dd[@class="mtit"]/a/@href')[0]

            pub_date = column.xpath('./dd[@class="mexp"]/span')[0].text_content()
            yesterday = datetime.datetime.today()-datetime.timedelta(days=1)
            before_yesterday = datetime.datetime.today()-datetime.timedelta(days=2)
            pub_date = pub_date.replace("昨天", yesterday.strftime("%Y-%m-%d"))
            pub_date = pub_date.replace("前天", before_yesterday.strftime("%Y-%m-%d"))
            # print(title, link, pub_date)

            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            detail_body = requests.get(link).text
            if detail_body:
                article = self._parse_detail(detail_body)
                if article:
                    item['article'] = self._process_content(article)
                    # print(item)
                    items.append(item)
        # print(num)
        return items


if __name__ == "__main__":
    column = STCN_Column()
    column._start()
