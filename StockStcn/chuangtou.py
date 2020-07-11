from lxml import html

from StockStcn.base_stcn import STCN_Base
from StockStcn import stcn_utils as utils


class STCN_ChuangTou(STCN_Base):
    # 创投
    def __init__(self):
        super(STCN_ChuangTou, self).__init__()
        self.format_url = "http://news.stcn.com/xwct/{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 21
        self.name = '创投'

    def _parse_list_body(self, body):
        '''
<ul class="news_list">
            <li>
        <p class="tit"><a href="http://news.stcn.com/2020/0224/15657601.shtml" target="_blank" title="高瓴资本宣布成立“高瓴创投” 首期规模100亿">高瓴资本宣布成立“高瓴创投” 首期规模100亿</a></p>
        <p class="exp">高瓴资本在其官方公众号发布“致创业者的一封信”，宣布成立专注于投资早期创业公司的高瓴创投，主要专注于生物医药及医疗器械、软件服务和原发科技创新、消费互联网及科技、新兴消费品牌及服务四大领域的风险投资。</p>
        <p class="sj">2020-02-24<span>12:00</span></p>
    </li>
        '''
        # print(body)
        # with open("hello.html", "w") as f:
        #     f.write(body)
        # sys.exit(0)
        doc = html.fromstring(body)
        items = utils.parse_list_items_1(doc)
        [self._add_article(item) for item in items]
        # print(len(items))
        return items


if __name__ == "__main__":
    ct = STCN_ChuangTou()
    ct._start()
