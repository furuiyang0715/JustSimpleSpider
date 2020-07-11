from lxml import html

from StockStcn.base_stcn import STCN_Base
from StockStcn import stcn_utils as utils


class STCN_SSGSYQB(STCN_Base):
    # 上市公司舆情榜
    def __init__(self):
        super(STCN_SSGSYQB, self).__init__()
        self.list_url = "http://yq.stcn.com/ssgsyqb/"
        self.name = '上市公司舆情榜'

    def _parse_list_body(self, body):
        '''
<ul id="news_list2">
    <li>
        <p class="yq_tit">
            <a href="http://yq.stcn.com/2020/0221/15653999.shtml" target="_blank" title="光大银行开通“抗击疫情”绿色通道">
                <span>光大银行开通“抗击疫情”绿色通道</span>
            </a>
            <em>2020-02-21 17:42</em>
        </p>
        <p class="yq_exp">光大银行深圳分行所有营业网点开通了“抗击疫情”绿色通道</p>
    </li>
        '''
        # print(body)

        # sys.exit(0)

        doc = html.fromstring(body)
        items = utils.parse_list_items_5(doc)
        [self._add_article(item) for item in items]
        # print(len(items))
        return items


if __name__ == "__main__":
    stcn_ssgsyqb = STCN_SSGSYQB()
    stcn_ssgsyqb._start()
