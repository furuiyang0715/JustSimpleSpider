import sys

from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base
from PublicOpinion.stcn import stcn_utils as utils


class STCN_GSDT(STCN_Base):
    # 公司动态
    def __init__(self):
        super(STCN_GSDT, self).__init__()
        self.format_url = "http://company.stcn.com/gsdt/{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 21
        self.name = '公司动态'

    def _parse_list_body(self, body):
        '''
 <ul class="news_list2" id="news_list2">
    <li >
        <a href="http://company.stcn.com/2020/0226/15683561.shtml" target="_blank" title="中电兴发首发自主可控视频综合管理系统">中电兴发首发自主可控视频综合管理系统</a>
        <span>2020-02-26<i>13:03</i></span>
    </li>
        '''
        # print(body)
        # sys.exit(0)

        doc = html.fromstring(body)
        items = utils.parse_list_items_3(doc)
        [self._add_article(item) for item in items]
        # print(len(items))
        return items


if __name__ == "__main__":
    gs = STCN_GSDT()
    gs._start()
