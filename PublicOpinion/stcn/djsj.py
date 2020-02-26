import sys

from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base
from PublicOpinion.stcn import stcn_utils as utils


class STCN_DJSJ(STCN_Base):
    # 独家数据
    def __init__(self):
        super(STCN_DJSJ, self).__init__()
        self.format_url = "http://data.stcn.com/djsj/{}.shtml"
        self.pages = True  # 是否需要翻页
        self.page_num = 21
        self.name = '独家数据'

    def _parse_list_body(self, body):
        '''
<ul id="news_list2">
    <li >
        <a href="http://data.stcn.com/2020/0225/15682792.shtml" target="_blank" title="罕见黄金坑？千亿科技龙头玩刺激，主力抢买股曝光 （附股）">罕见黄金坑？千亿科技龙头玩刺激，主力抢买股曝光 （附股）</a>
        <span>2020-02-25<i>20:34</i></span>
    </li>
        '''
        # print(body)
        # with open("hello.html", "w") as f:
        #     f.write(body)
        # sys.exit(0)
        doc = html.fromstring(body)
        items = utils.parse_list_items_3(doc)
        [self._add_article(item) for item in items]
        # print(len(items))
        return items


if __name__ == "__main__":
    dj = STCN_DJSJ()
    dj._start()
