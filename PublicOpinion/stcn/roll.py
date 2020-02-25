from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base


class STCN_Roll(STCN_Base):
    # 滚动
    def __init__(self):
        super(STCN_Roll, self).__init__()
        self.format_url = "http://news.stcn.com/roll/index_{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 21

    def _parse_list_body(self, body):
        items = []
        doc = html.fromstring(body)
        columns = doc.xpath("//ul[@id='news_list2']/li")
        num = 0
        for column in columns:
            num += 1
            title = column.xpath("./a")[-1].xpath("./@title")[0]
            link = column.xpath("./a")[-1].xpath("./@href")[0]
            pub_date = column.xpath("./span")[0].text_content()
            pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            items.append(item)
        [self._add_article(item) for item in items]
        print(len(items))
        return items


if __name__ == "__main__":
    kuaixun = STCN_Roll()
    kuaixun._start()
