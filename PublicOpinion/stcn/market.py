import pprint
import sys

from lxml import html

from PublicOpinion.stcn.base_stcn import STCN_Base
from PublicOpinion.stcn import stcn_utils as utils


class STCN_Market(STCN_Base):
    # 股市
    def __init__(self):
        super(STCN_Market, self).__init__()
        self.list_url = "http://stock.stcn.com/"
        self.name = '股市'

    def _parse_list_body(self, body):
        # print(body)
        doc = html.fromstring(body)
        items = utils.parse_list_items_1(doc)
        [self._add_article(item) for item in items]
        # print(pprint.pformat(items))
        return items


if __name__ == "__main__":
    market = STCN_Market()
    market._start()
