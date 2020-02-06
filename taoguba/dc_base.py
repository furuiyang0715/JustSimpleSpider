import logging

import pymysql

from taoguba.configs import DC_HOST, DC_PORT, DC_USER, DC_PASSWD, DC_DB


logger = logging.getLogger()


class DCSpider(object):
    """
    与数据中心配置相关
    """
    @property
    def keys(self):   # {'300150.XSHE': '世纪瑞尔',
        """
        从 datacanter.const_secumain 数据库中获取当天需要爬取的股票信息
        返回的是 股票代码: 中文名简称 的字典的形式
        """
        try:
            conn = pymysql.connect(host=DC_HOST, port=DC_PORT, user=DC_USER,
                                   passwd=DC_PASSWD, db=DC_DB)
        except Exception as e:
            logger.warning(f"connect [datacenter.const_secumain] to get secucode info today fail, {e}")
            raise

        cur = conn.cursor()
        cur.execute("USE datacenter;")
        cur.execute("""select SecuCode, ChiNameAbbr from const_secumain where SecuCode \
        in (select distinct SecuCode from const_secumain);""")
        keys = {r[0]: r[1] for r in cur.fetchall()}
        cur.close()
        conn.close()
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
    def lowerkeys(self):  # {sz000651: "格力电器", ...}
        """
        将数据库中查询出的股票代码转换为可用于 url 查询的小写前缀模式
        :return:
        """
        try:
            conn = pymysql.connect(host=DC_HOST, port=DC_PORT, user=DC_USER,
                                   passwd=DC_PASSWD, db=DC_DB)
        except Exception as e:
            logger.warning(f"connect [datacenter.const_secumain] to get secucode info today fail, {e}")
            raise

        cur = conn.cursor()
        cur.execute("USE datacenter;")
        cur.execute("""select SecuCode, ChiNameAbbr from const_secumain where SecuCode \
                   in (select distinct SecuCode from const_secumain);""")

        keys = {self.convert_lower(r[0]): r[1] for r in cur.fetchall()}
        cur.close()
        conn.close()
        return keys


if __name__ == "__main__":
    d = DCSpider()
    print(d.lowerkeys)