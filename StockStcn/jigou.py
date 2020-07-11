# 重复

# from lxml import html
#
# from PublicOpinion.StockStcn import stcn_utils as utils
# from PublicOpinion.StockStcn.base_stcn import STCN_Base
#
#
# class STCN_FINANCE(STCN_Base):
#     # 证券时报-机构
#     def __init__(self):
#         super(STCN_FINANCE, self).__init__()
#         self.list_url = "http://finance.stcn.com/"
#         self.name = '机构'
#
#     def _parse_list_body(self, body):
#         doc = html.fromstring(body)
#         first = utils.parse_list_first(doc)
#         self._add_article(first)
#
#         columns = utils.parse_list_items_1(doc)
#         for column in columns:
#             self._add_article(column)
#
#         columns.append(first)
#         return columns
#
#
# if __name__ == "__main__":
#     c = STCN_FINANCE()
#     c._start()
