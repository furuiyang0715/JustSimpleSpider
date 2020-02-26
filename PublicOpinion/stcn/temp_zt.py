from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base


class STCN_ZT(STCN_Base):
    def __init__(self):
        super(STCN_ZT, self).__init__()
        self.list_url = "http://zt.stcn.com/"

    def _parse_second_list(self, body):
        doc = html.fromstring(body)
        ret = doc.xpath("//div[@class='hot']")[0]
        first = {}
        link = ret.xpath("//h2/a/@href")[0]
        title = ret.xpath("//h2/a/@title")[0]
        first['link'] = link
        first['title'] = title
        return first

    def _parse_first_list(self, body):
        links = []
        doc = html.fromstring(body)
        items = []
        first = doc.xpath("//dl[@class='hotNews']")[0]
        link = first.xpath("//dt/a/@href")[0]
        links.append(link)

        # 列表文章
        columns = doc.xpath("//div[@class='news_list']/dl")
        num = 0
        for column in columns:
            num += 1
            link = column.xpath("./dd[@class='tit']/a/@href")[0]
            links.append(link)
        print("num is ", num)
        return links

    def _start(self):
        first_list_page = self._get(self.list_url)
        if first_list_page:
            links = self._parse_first_list(first_list_page)
            print(links)
            for first_list_url in links:
                second_list_page = self._get(first_list_url)
                if second_list_page:
                    items = self._parse_second_list(second_list_page)
                    print(items)
