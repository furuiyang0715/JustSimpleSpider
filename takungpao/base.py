import logging
import traceback

from takungpao.configs import (SPIDER_MYSQL_HOST, SPIDER_MYSQL_PORT, SPIDER_MYSQL_USER,
                               SPIDER_MYSQL_PASSWORD, SPIDER_MYSQL_DB, PRODUCT_MYSQL_HOST,
                               PRODUCT_MYSQL_PORT, PRODUCT_MYSQL_USER, PRODUCT_MYSQL_PASSWORD,
                               PRODUCT_MYSQL_DB, JUY_HOST, JUY_PORT, JUY_USER, JUY_PASSWD, JUY_DB,
                               DC_HOST, DC_PORT, DC_USER, DC_PASSWD, DC_DB)
from takungpao.sql_pool import PyMysqlPoolBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Base(object):
    spider_cfg = {  # 爬虫库
        "host": SPIDER_MYSQL_HOST,
        "port": SPIDER_MYSQL_PORT,
        "user": SPIDER_MYSQL_USER,
        "password": SPIDER_MYSQL_PASSWORD,
        "db": SPIDER_MYSQL_DB,
    }

    product_cfg = {  # 正式库
        "host": PRODUCT_MYSQL_HOST,
        "port": PRODUCT_MYSQL_PORT,
        "user": PRODUCT_MYSQL_USER,
        "password": PRODUCT_MYSQL_PASSWORD,
        "db": PRODUCT_MYSQL_DB,
    }

    # 聚源数据库
    juyuan_cfg = {
        "host": JUY_HOST,
        "port": JUY_PORT,
        "user": JUY_USER,
        "password": JUY_PASSWD,
        "db": JUY_DB,
    }

    # 数据中心库
    dc_cfg = {
        "host": DC_HOST,
        "port": DC_PORT,
        "user": DC_USER,
        "password": DC_PASSWD,
        "db": DC_DB,
    }

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/79.0.3945.117 Safari/537.36'
        }

    def _init_pool(self, cfg: dict):
        """
        eg.
        conf = {
                "host": LOCAL_MYSQL_HOST,
                "port": LOCAL_MYSQL_PORT,
                "user": LOCAL_MYSQL_USER,
                "password": LOCAL_MYSQL_PASSWORD,
                "db": LOCAL_MYSQL_DB,
        }
        :param cfg:
        :return:
        """
        pool = PyMysqlPoolBase(**cfg)
        return pool

    def contract_sql(self, to_insert: dict, table: str, update_fields: list):
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}` '''.format(table) + fields_str + ''' values ''' + values_str
        on_update_sql = ''' ON DUPLICATE KEY UPDATE '''
        update_vs = []
        for update_field in update_fields:
            on_update_sql += '{}=%s,'.format(update_field)
            update_vs.append(to_insert.get(update_field))
        on_update_sql = on_update_sql.rstrip(",")
        sql = base_sql + on_update_sql + """;"""
        vs.extend(update_vs)
        return sql, tuple(vs)

    def _save(self, sql_pool, to_insert, table, update_fields):
        try:
            insert_sql, values = self.contract_sql(to_insert, table, update_fields)
            count = sql_pool.insert(insert_sql, values)
        except:
            traceback.print_exc()
            logger.warning("失败")
        else:
            if count == 1:  # 插入新数据的时候结果为 1
                logger.info("插入新数据 {}".format(to_insert))

            elif count == 2:
                logger.info("刷新数据 {}".format(to_insert))

            else:  # 数据已经存在的时候结果为 0
                # logger.info(count)
                logger.info("已有数据 {} ".format(to_insert))

            sql_pool.end()
            return count

    # def _get_proxy(self):
    #     if self.local:
    #         return requests.get(LOCAL_PROXY_URL).text.strip()
    #     else:
    #         random_num = random.randint(0, 10)
    #         if random_num % 2:
    #             time.sleep(1)
    #             return requests.get(PROXY_URL).text.strip()
    #         else:
    #             return requests.get(LOCAL_PROXY_URL).text.strip()

    # def get(self, url):
    #     if not self.use_proxy:
    #         return requests.get(url, headers=self.headers)
    #
    #     count = 0
    #     while True:
    #         count += 1
    #         if count > 10:
    #             return None
    #         try:
    #             proxy = {"proxy": self._get_proxy()}
    #             print("proxy is >> {}".format(proxy))
    #             resp = requests.get(url, headers=self.headers, proxies=proxy)
    #         except:
    #             traceback.print_exc()
    #             time.sleep(0.5)
    #         else:
    #             if resp.status_code == 200:
    #                 return resp
    #             elif resp.status_code == 404:
    #                 return None
    #             else:
    #                 print("status_code: >> {}".format(resp.status_code))
    #                 time.sleep(1)
    #                 pass
    #
    # def convert_dt(self, time_stamp):
    #     d = str(datetime.datetime.fromtimestamp(time_stamp))
    #     return d
