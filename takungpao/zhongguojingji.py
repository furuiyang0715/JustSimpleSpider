import datetime
import sys

from gne import GeneralNewsExtractor
from lxml import html

sys.path.append("./../../")
from takungpao.hkstock_cjss import Base


class ZhongGuoJingJi(Base):

    def __init__(self):
        super(ZhongGuoJingJi, self).__init__()
        self.name = '中国经济'
        self.first_url = 'http://www.takungpao.com/finance/236132/index.html'
        self.format_url = 'http://www.takungpao.com/finance/236132/{}.html'
        self.page = 10
        self.fields = ['pub_date', 'link', 'title', 'article']
        self.table = 'takungpao'
        self.extractor = GeneralNewsExtractor()

    def _process_pub_dt(self, pub_date):
        # 对 pub_date 的各类时间格式进行统一
        current_dt = datetime.datetime.now()
        yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        after_yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        if "小时前" in pub_date:  # eg. 20小时前
            hours = int(pub_date.replace('小时前', ''))
            pub_date = (current_dt - datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        elif "昨天" in pub_date:  # eg. 昨天04:24
            pub_date = pub_date.replace('昨天', '')
            pub_date = " ".join([yesterday_dt_str, pub_date])
        elif '前天' in pub_date:  # eg. 前天11:33
            pub_date = pub_date.replace("前天", '')
            pub_date = " ".join([after_yesterday_dt_str, pub_date])
        else:  # eg. 02-29 04:24
            pub_date = str(current_dt.year) + '-' + pub_date
        # print(pub_date)
        return pub_date

    def _parse_detail(self, link):
        detail_resp = self.get(link)
        if detail_resp:
            body = detail_resp.text
            result = self.extractor.extract(body)
            content = result.get("content")
            return content

    def _parse_list(self, list_url):
        items = []
        list_resp = self.get(list_url)
        if list_resp:
            list_page = list_resp.text
            doc = html.fromstring(list_page)
            news_list = doc.xpath('//div[@class="wrap_left"]/dl[@class="item clearfix"]')
            for news in news_list:
                item = {}
                link = news.xpath('./dd[@class="intro"]/a/@href')[0]
                # print(link)
                item['link'] = link

                title = news.xpath("./dd/a/@title")[0]
                # print(title)
                item['title'] = title

                pub_date = news.xpath("./dd[@class='sort']/text()")[0]
                pub_date = self._process_pub_dt(pub_date)
                # print(pub_date)
                item['pub_date'] = pub_date

                article = self._parse_detail(link)
                if article:
                    article = self._process_content(article)
                    item['article'] = article
                    print(item)
                    items.append(item)
        return items

    def _start(self):

        for page in range(1, self.page + 1):
            print("page >>>", page)
            if page == 1:
                list_url = self.first_url
            else:
                list_url = self.format_url.format(page)
            items = self._parse_list(list_url)
            self.save(items)


if __name__ == "__main__":

    zg = ZhongGuoJingJi()
    zg.start()
