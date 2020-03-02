import sys

from gne import GeneralNewsExtractor
from lxml import html

from PublicOpinion.takungpao.hkstock_cjss import Base


class Travel(Base):
    def __init__(self):
        super(Travel, self).__init__()
        self.first_url = 'http://finance.takungpao.com/travel/index.html'
        self.format_url = 'http://finance.takungpao.com/travel/index_{}.html'
        self.name = '旅游'
        self.table = 'takungpao'
        self.fields = ['link', 'title', 'pub_date', 'article']
        self.extractor = GeneralNewsExtractor()
        self.page = 19

    # def _parse_detail(self, body):
    #     try:
    #         result = self.extractor.extract(body)
    #         content = result.get("content")
    #         return content
    #     except:
    #         print("解析详情页失败 ..")
    #         return None

    def _parse_page(self, body):
        '''
<div class="tpk_text clearfix">
    <p align="center"><img src="http://images.takungpao.com/2016/0222/20160222100957613.jpg" style="width: 550px; height: 366px"></p>
    <p style="text-align: center">2016年2月19日报道（具体拍摄时间不详），海洋生物学家Christoph Rohner在坦桑尼亚马菲亚岛海底拍摄到一组鲸鲨进食的画面。画面中这条鲸鲨张大嘴巴让小鱼无路可逃，纷纷成了这条海洋猎手的口中餐。图片来源：东方IC 版权作品 请勿转载</p>
</div>
        '''
        doc = html.fromstring(body)
        content = doc.xpath('//div[@class="tpk_text clearfix"]')[0].text_content()
        # print(content)
        # sys.exit(0)
        return content.strip()

    def _parse_detail(self, link, body):
        # 很多页 每页图片下面是字的模式
        '''
<div class="tpk_page clearfix">
    <span class="firstpage">1</span>
    <a href="http://finance.takungpao.com/travel/2016-02/3282833_2.html">2</a>
    <a href="http://finance.takungpao.com/travel/2016-02/3282833_3.html">3</a>
    <a class="a1" href="http://finance.takungpao.com/travel/2016-02/3282833_2.html">下一页</a>
</div>
        '''
        content1 = self._parse_page(body)
        # print(content1)

        doc = html.fromstring(body)
        page_num_info = doc.xpath('//div[@class="tpk_page clearfix"]')

        # if not page_num_info:
        #     return content1

        page_info = page_num_info[0].text_content()

        # 多页图集
        page_info_list = page_info.split()
        # print(">>>", page_info_list)
        if not page_info_list:
            return content1

        max_page = int(page_info_list[-2].replace("..", ''))
        contents = []
        for j in range(2, max_page+1):
            l = link.replace(".html", "_{}.html".format(j))
            m_resp = self.get(l)
            if m_resp:
                m_body = m_resp.text
                cont = self._parse_page(m_body)
                contents.append(cont)

        contents.insert(0, content1)
        return ''.join(contents)

    def _parse_list(self, body):
        doc = html.fromstring(body)
        news_list = doc.xpath('//div[@class="txtImgListeach current"]')
        # print(len(news_list))

        items = []
        for news in news_list:
            item = {}
            link = news.xpath("./h3/a/@href")[0]
            # print(link)
            item['link'] = link
            title = news.xpath("./h3/a")[0].text_content()
            # print(title)
            item['title'] = title
            pub_date = news.xpath(".//span[@class='time']")[0].text_content()
            # print(pub_date)
            item['pub_date'] = pub_date

            detail_resp = self.get(link)
            # print("<<<", link)
            if detail_resp:
                detail_page = detail_resp.text
                article = self._parse_detail(link, detail_page)
                if article:
                    article = self._process_content(article)
                    item['article'] = article
                    print(item)
                    items.append(item)
        return items

    def _start(self):
        for page in range(1, self.page+1):
            if page == 1:
                list_url = self.first_url
            else:
                list_url = self.format_url.format(page)
            list_resp = self.get(list_url)
            if list_resp:
                list_page = list_resp.text
                items = self._parse_list(list_page)
                self.save(items)


if __name__ == "__main__":
    t = Travel()
    t.start()

    # _url = "http://finance.takungpao.com/travel/2016-02/3282833.html"
    # http://finance.takungpao.com/travel/2016-02/3282833_2.html
    # http://finance.takungpao.com/travel/2016-02/3282833_3.html
    # body = t.get(_url).text
    # ret = t._parse_detail(_url, body)
    # print(ret)
