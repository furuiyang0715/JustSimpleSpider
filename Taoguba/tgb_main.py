from Taoguba.taoguba import Taoguba
from base import SpiderBase


class TgbSchedule(SpiderBase):
    table_name = 'taoguba'
    dt_benchmark = 'pub_date'

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

    def start(self):
        for code, name in self.lower_keys.items():
            print(code, name)
            Taoguba(name, code).start()


if __name__ == "__main__":
    TgbSchedule().start()
