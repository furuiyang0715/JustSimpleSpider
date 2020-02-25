import sys

from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base


class STCN_FINANCE(STCN_Base):
    def __init__(self):
        super(STCN_FINANCE, self).__init__()
        self.list_url = "http://kcb.stcn.com/news/index.shtml"

    def _parse_list_body(self, body):
        print(body)
        doc = html.fromstring(body)
        items = []
        # 题头文章
        first = doc.xpath("//dl[@class='hotNews']")[0]
        title = first.xpath("//dt/a/@title")[0]
        link = first.xpath("//dt/a/@href")[0]
        pub_date = first.xpath("//dd[@class='sj']")[0].text_content()
        pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
        first = dict()
        first['title'] = title
        first['link'] = link
        first['pub_date'] = pub_date
        detail_body = self._get(link)
        if detail_body:
            article = self._parse_detail(detail_body)
            if article:
                first['article'] = article
                items.append(first)

        print(first)