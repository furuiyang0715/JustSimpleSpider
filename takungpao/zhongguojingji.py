import datetime
import sys
import traceback

from lxml import html

sys.path.append("./../../")
from takungpao.base import logger, Base


class ZhongGuoJingJi(Base):
    def __init__(self):
        super(ZhongGuoJingJi, self).__init__()
        self.name = '中国经济'
        self.first_url = 'http://www.takungpao.com/finance/236132/index.html'
        self.format_url = 'http://www.takungpao.com/finance/236132/{}.html'

    def _parse_total_page(self, link):
        '''
        <div class="tkp_page">
            <a href="/finance/236132/index.html" class="cms_prevpage">上一页</a>
            <div class="cms_curpage">1</div>
            <a href="/finance/236132/2.html" class="cms_page">2</a>
            <a href="/finance/236132/3.html" class="cms_page">3</a>
            <a href="/finance/236132/4.html" class="cms_page">4</a>
            <a href="/finance/236132/5.html" class="cms_page">5</a>
            <a href="/finance/236132/6.html" class="cms_page">6</a>
            <a href="/finance/236132/7.html" class="cms_page">7</a>
            <a href="/finance/236132/8.html" class="cms_page">8</a>
            <a href="/finance/236132/9.html" class="cms_page">9</a>
            <a href="/finance/236132/10.html" class="cms_page">10</a>
            <a href="/finance/236132/2.html" class="cms_nextpage">下一页</a>
        </div>
        '''
        list_resp = self.get(link)
        if list_resp:
            body = list_resp.text
            doc = html.fromstring(body)
            page = int(doc.xpath("//div[@class='tkp_page']/a[@class='cms_page']")[-1].text_content())
            return page

    def _parse_detail(self, link):
        """解析详情页内容
        """
        '''
        <div class="tkp_con_author"><span>2020-05-16 04:24:25</span><span>大公报</span> </div>
        '''

        '''
        <h2 class="tkp_con_author">時間：
            <span style="color:#666; margin-right:35px;">2020-04-23 11:15:32</span>來源：
            <span style="color:#666;">
                <a href="http://www.takungpao.com/" target="_blank" style="color:#AAA">大公网</a>
            </span>
        </h2>
        '''
        detail_resp = self.get(link)
        if detail_resp:
            body = detail_resp.text
            doc = html.fromstring(body)
            try:
                source = doc.xpath("//div[@class='tkp_con_author']/span")[-1].text_content()
            except:
                try:
                    source = doc.xpath("//h2[@class='tkp_con_author']/span")[-1].text_content()
                except:
                    source = '大公报'

            result = self.extractor.extract(body)
            content = result.get("content")
            return {"source": source, "content": content}
        else:
            return {}

    def _parse_list(self, list_url):
        list_resp = self.get(list_url)
        if list_resp:
            list_page = list_resp.text
            doc = html.fromstring(list_page)
            news_list = doc.xpath('//div[@class="wrap_left"]/dl[@class="item clearfix"]')
            for news in news_list:
                item = {}
                link = news.xpath('./dd[@class="intro"]/a/@href')[0]
                item['link'] = link

                title = news.xpath("./dd/a/@title")[0]
                title = self._process_content(title)
                # 去除其中的字节顺序标记符
                title = title.replace("\ufeff", '')
                item['title'] = title

                pub_date = news.xpath("./dd[@class='sort']/text()")[0]
                pub_date = self._process_pub_dt(pub_date)
                item['pub_date'] = pub_date

                ret = self._parse_detail(link)
                item['article'] = ret.get("content")
                item['source'] = ret.get("source")
                logger.info(item)

    def _start(self):
        page = self._parse_total_page(self.first_url)
        logger.info("总页数 {}".format(page))
        for page in range(1, page+1):
            logger.info("PAGE {}".format(page))
            if page == 1:
                list_url = self.first_url
            else:
                list_url = self.format_url.format(page)
            self._parse_list(list_url)

    def start(self):
        try:
            self._start()
        except Exception as e:
            raise e


if __name__ == "__main__":
    zg = ZhongGuoJingJi()
    try:
        zg.start()
    except:
        traceback.print_exc()
