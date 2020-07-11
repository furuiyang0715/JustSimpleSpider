import datetime
import sys

from Taoguba.taoguba import Taoguba
from base import SpiderBase


class TgbSchedule(SpiderBase):
    @property
    def keys(self):
        self._dc_init()
        sql = '''select SecuCode, ChiNameAbbr from const_secumain where SecuCode in (select distinct SecuCode from const_secumain); '''
        datas = self.dc_client.select_all(sql)
        keys = {r['SecuCode']: r['ChiNameAbbr'] for r in datas}
        return keys

    def convert_lower(self, order_book_id: str):
        """
        转换合约代码为前缀模式 并且前缀字母小写
        :param order_book_id:
        :return:
        """
        EXCHANGE_DICT = {
            "XSHG": "SH",
            "XSHE": "SZ",
            "INDX": "IX",
            "XSGE": "SF",
            "XDCE": "DF",
            "XZCE": "ZF",
            "CCFX": "CF",
            "XINE": "IF",
        }

        code, exchange = order_book_id.split('.')
        ex = EXCHANGE_DICT.get(exchange)
        return ''.join((ex, code)).lower()

    @property
    def lower_keys(self):
        lkeys = {}
        for key, value in self.keys.items():
            lkeys[self.convert_lower(key)] = value
        return lkeys

    # def ins_start(self, code):
    #     name = self.lower_keys.get(code)
    #     if not name:
    #         print(">> ", code)
    #         return
    #     instance = Taoguba(name=name, code=code)
    #     print(">>>{} {}".format(code, name))
    #     instance.start()

    # def start(self):
    #     code_list = list(self.lower_keys.keys())
    #     random.shuffle(code_list)
    #
    #     for code in code_list:
    #         name = lower_keys.get(code)
    #         if not name:
    #             print(">> ", code)
    #             continue
    #         instance = Taoguba(name=name, code=code)
    #         print(">>>{} {}".format(code, name))
    #         instance.start()
    #
    #     pool = threadpool.ThreadPool(4)
    #     reqs = threadpool.makeRequests(self.ins_start, code_list)
    #     [pool.putRequest(req) for req in reqs]
    #     pool.wait()


if __name__ == "__main__":
    tgbs = TgbSchedule()
    for k, v in tgbs.lower_keys.items():
        print(k, v)
        tt = Taoguba(v, k)
        tt.start()
        sys.exit(0)
