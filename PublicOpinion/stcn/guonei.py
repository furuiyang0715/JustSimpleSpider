import sys

from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base
from PublicOpinion.stcn import stcn_utils as utils


class STCN_GuoNei(STCN_Base):
    # 国内
    def __init__(self):
        super(STCN_GuoNei, self).__init__()
        self.format_url = "http://news.stcn.com/guonei/{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 4623

    def _parse_list_body(self, body):
        '''
<ul class="news_list">
    <li>
        <p class="tit"><a href="http://news.stcn.com/2020/0225/15682787.shtml" target="_blank" title="新零售商家加快复工复产 菜鸟急调400辆车驰援商家发货">新零售商家加快复工复产 菜鸟急调400辆车驰援商家发货</a></p>
        <p class="exp"></p>
        <p class="sj">2020-02-25<span>20:32</span></p>
    </li>
        '''
        # print(body)
        # sys.exit(0)
        doc = html.fromstring(body)
        items = utils.parse_list_items_1(doc)
        [self._add_article(item) for item in items]
        print(len(items))
        return items


if __name__ == "__main__":
    guonei = STCN_GuoNei()
    guonei._start()
