import logging

import pymysql

from PublicOpinion.configs import DC_HOST, DC_PORT, DC_USER, DC_PASSWD, DC_DB

logger = logging.getLogger()


class TaogubaBase(object):

    @property
    def keys(self):  # {'300150.XSHE': '世纪瑞尔',
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


if __name__ == "__main__":
    base = TaogubaBase()
    print(base.keys)