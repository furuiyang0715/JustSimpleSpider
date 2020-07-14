from lxml import html

from StockStcn.base_stcn import STCN_Base
from StockStcn import stcn_utils as utils


class STCN_Company(STCN_Base):
    def __init__(self):
        # 公司
        super(STCN_Company, self).__init__()
        self.list_url = "http://company.stcn.com/"
        self.name = '公司'

    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        first = utils.parse_list_first(doc)
        self._add_article(first)

        columns = utils.parse_list_items_1(doc)
        [self._add_article(column) for column in columns]
        columns.append(first)

        # print(len(columns))
        return columns


if __name__ == "__main__":
    d = STCN_Company()
    d._start()
