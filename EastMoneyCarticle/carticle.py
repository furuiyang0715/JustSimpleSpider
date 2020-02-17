# -*- coding: utf-8 -*-
import sys
import pprint
import json
import random
import re
import string
import time
import traceback
import pymysql
import requests
import logging

from lxml import html
from urllib.parse import urlencode
from requests.exceptions import ProxyError, Timeout, ConnectionError, ChunkedEncodingError

sys.path.insert(0, "./../")
from EastMoneyCarticle.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, \
    MYSQL_TABLE, DC_HOST, DC_PORT, DC_USER, DC_PASSWD, DC_DB, LIST_START, LIST_END
from EastMoneyCarticle.sql_pool import PyMysqlPoolBase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CArticle(object):
    def __init__(self, key):
        self.key = key
        self.start_url = 'http://api.so.eastmoney.com/bussiness/Web/GetSearchList?'
        self.page_size = 10
        self.headers = {
            "Referer": "http://so.eastmoney.com/CArticle/s?keyword={}".format(self.key.encode()),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",


        }
        self.db = MYSQL_DB
        self.table = MYSQL_TABLE
        conf = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "db": MYSQL_DB,
        }
        self.sql_pool = PyMysqlPoolBase(**conf)
        self.proxy = self.get_proxy()
        self.error_detail = []
        self.error_list = []

    def get_proxy(self):
        # r = requests.get('http://192.168.0.102:8888/get')
        r = requests.get('http://172.17.0.5:8888/get')
        proxy = r.text
        return proxy

    def crawl(self, url, proxy):
        proxies = {'http': proxy}
        r = requests.get(url, proxies=proxies, headers=self.headers, timeout=3)
        return r

    def get(self, url):
        count = 0
        while True:
            count = count + 1
            try:
                resp = self.crawl(url, self.proxy)
                if resp.status_code == 200:
                    return resp
                elif count >= 5:
                    logger.warning(f'抓取网页{url}最终失败')
                    break
                else:
                    self.proxy = self.get_proxy()
                    logger.info(f"无效状态码{resp.status_code}, 更换代理{self.proxy}\n")
            except (ChunkedEncodingError, ConnectionError, Timeout, UnboundLocalError, UnicodeError, ProxyError):
                self.proxy = self.get_proxy()
                logger.info(f'代理失败,更换代理{self.proxy} \n')

    def make_query_params(self, msg, page):
        """
        拼接动态请求参数
        """
        query_params = {
            'type': '8224',  # 该参数表明按时间排序
            'pageindex': str(page),
            'pagesize': str(self.page_size),
            'keyword': msg,
            'name': 'caifuhaowenzhang',
            'cb': 'jQuery{}_{}'.format(
                ''.join(random.choice(string.digits) for i in range(0, 21)),
                str(int(time.time() * 1000))
            ),
            '_': str(int(time.time() * 1000)),
        }
        return query_params

    def get_list(self, list_url):
        resp = self.get(list_url)
        if resp:
            return resp.text
        else:
            self.error_list.append(list_url)

    def get_detail(self, detail_url):
        resp = self.get(detail_url)
        if resp:
            return resp.text
        else:
            self.error_detail.append(detail_url)

    def parse_list(self, list_page):
        try:
            json_data = re.findall(r'jQuery\d{21}_\d{13}\((\{.*?\})\)', list_page)[0]
            list_data = json.loads(json_data).get("Data")
        except:
            return None
        else:
            if list_data:
                return list_data
            else:
                return []

    def contract_sql(self, to_insert):
        """
        根据待插入字典 拼接出对应的 sql 语句
        """
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}`.`{}` '''.format(
            self.db, self.table) + fields_str + ''' values ''' + values_str + ''';'''
        return base_sql, tuple(vs)

    def save(self, to_insert):
        try:
            insert_sql, values = self.contract_sql(to_insert)
            # count = self.sql_client.insert(insert_sql, values)
            count = self.sql_pool.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            logger.warning("重复 ")
            self.sql_pool.connection.rollback()
        except:
            logger.warning("失败")
            # traceback.print_exc()
            self.error_detail.append(to_insert.get("link"))
            self.sql_pool.connection.rollback()
            # 插入失败之后需要进行回滚

        else:
            return count

    def parse_detail(self, detail_page):
        doc = html.fromstring(detail_page)
        article_body = doc.xpath('//div[@class="article-body"]/*')
        contents = []
        for p_node in article_body:
            children = p_node.getchildren()
            children_tags = [child.tag for child in children]
            if children_tags and "img" in children_tags:
                img_links = p_node.xpath("./img/@src")  # list
                contents.append(",".join(img_links))
            else:
                contents.append(p_node.text_content())
        contents = "\r\n".join(contents)
        return contents

    # def process_item(self, item):
    #     return item

    def _exist(self, link):
        ret = self.sql_pool.select_one(f"select * from {self.table} where link = '{link}';")
        if ret:
            return True
        else:
            return False

    def __del__(self):
        print("数据库提交 释放资源")
        try:
            self.sql_pool.dispose()
        except:
            pass

    def close(self):
        print("手动关闭资源")
        try:
            self.sql_pool.dispose()
        except:
            pass

    def select_key_links(self):
        select_all_sql = f"select link from {self.table} where code = '{self.key}' and article is NULL;"
        # links = self.sql_pool.select_many(select_all_sql, size=10)
        links = self.sql_pool.select_all(select_all_sql)
        return links

    def update_detail(self, link, artilce):
        update_sql = f"update {self.table} set article = '{artilce}' where link = '{link}';"
        # print(update_sql)
        ret = self.sql_pool.update(update_sql)
        return ret

    def _run_page(self, page):
        list_url = self.start_url + urlencode(self.make_query_params(self.key, page))
        list_page = self.get_list(list_url)
        if list_page:
            list_gener = self.parse_list(list_page)  # list
            if not list_gener:
                logger.info(f"{self.key} 爬取完毕 ")
                return

            for data in list_gener:
                item = dict()
                item['code'] = self.key
                link = data.get("ArticleUrl")
                if self._exist(link):
                    logger.info("pass")
                    continue
                item['link'] = data.get("ArticleUrl")
                item['title'] = data.get("Title")
                item['pub_date'] = data.get("ShowTime")
                print("item", item)
                ret = self.save(item)
                if not ret:
                    logger.warning(f"插入失败 {item}")
            self.sql_pool.connection.commit()
            print(f"第{page}页保存成功")
            return page


class Schedule(object):
    def __init__(self):
        self.keys = sorted(self.dc_info().values())

    def dc_info(self):  # {'300150.XSHE': '世纪瑞尔',
        """
        从 datacanter.const_secumain 数据库中获取当天需要爬取的股票信息
        返回的是 股票代码: 中文名简称 的字典的形式
        """
        try:
            conn = pymysql.connect(host=DC_HOST, port=DC_PORT, user=DC_USER,
                                   passwd=DC_PASSWD, db=DC_DB)
        except Exception as e:
            raise

        cur = conn.cursor()
        cur.execute("USE datacenter;")
        cur.execute("""select SecuCode, ChiNameAbbr from const_secumain where SecuCode \
            in (select distinct SecuCode from const_secumain);""")
        dc_info = {r[0]: r[1] for r in cur.fetchall()}
        cur.close()
        conn.close()
        return dc_info

    def insert_list_info(self, key):
        c = CArticle(key)
        now = lambda: time.time()
        t1 = now()
        cur = t1
        for page in range(1, 50000):
            page = c._run_page(page)
            if not page:
                break
            print(f"第 {page} 页, 累计用时 {now() - t1}, 当前页用用时 {now() - cur} ")
            cur = now()
        c.close()
        with open("record.txt", "a+") as f:
            f.write(f"{key}: error_list: {c.error_list}, error_detail: {c.error_detail}\r\n")

    def run_detail(self, start, end):
        for key in self.keys[start: end]:
            c = CArticle(key)
            links = c.select_key_links()
            count = 0
            for link_info in links:
                link = link_info.get("link")
                print(key, link)
                try:
                    detail_page = c.get_detail(link)
                    artilce = c.parse_detail(detail_page)
                    ret = c.update_detail(link, artilce)
                    if ret:
                        print("更新成功")
                    else:
                        print("更新失败")
                    count += 1
                    if count > 10:
                        c.sql_pool.connection.commit()
                        count = 0
                except:
                    c.error_detail.append(link)

            with open("tell.txt", "a+") as f:
                f.write(f"{key}: error_detail: {c.error_detail}\r\n")

        with open("tell.txt", "r") as f:
            lines = f.readlines()
            print(pprint.pformat(lines))

    def run_list(self, start, end):
        # print(self.keys)
        for key in self.keys[start: end]:
            print(key)
            self.insert_list_info(key)

        with open("record.txt", "r") as f:
            lines = f.readlines()
            print(pprint.pformat(lines))


if __name__ == "__main__":
    schedule = Schedule()
    # print(schedule.keys)
    # print(schedule.keys.index("长春经开"))
    # print(len(schedule.keys))
    # schedule.run_list(LIST_START, LIST_END)

    schedule.run_detail(LIST_START, LIST_END)

    """
    docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/emm:v1 .
    
    docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/emm:v1
    
    sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/emm:v1
    
    sudo docker run -itd --name ins --env LIST_START=0 \
    --env LIST_END=10 \
    registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/emm:v1 
    
    sudo docker run -itd --name ins2 --env LIST_START=10 \
    --env LIST_END=100 \
    registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/emm:v1 
    
    sudo docker run -itd --name ins3 --env LIST_START=100 \
    --env LIST_END=200 \
    registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/emm:v1 
    
    sudo docker run -itd --name ins4 --env LIST_START=200 \
    --env LIST_END=1000 \
    registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/emm:v1 
    
    sudo docker run -itd --name ins5 --env LIST_START=1000 \
    --env LIST_END=1500 \
    registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/emm:v1 
    
     sudo docker run -itd --name ins6 --env LIST_START=1500 \
    --env LIST_END=2000 \
    registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/emm:v1
    
    sudo docker run -itd --name last --env LIST_START=-100 \
    --env LIST_END=-1 \
    registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/emm:v1 
    
    sudo docker run -itd --name last --env LIST_START=-500 \
    --env LIST_END=-100 \
    registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/emm:v1 
    
    sudo docker logs -ft --tail 1000 ins
    """

    """
    !988
    use little_crawler; 
    select count(1) from eastmoney_carticle;
    select count(1) from eastmoney_carticle where code = "万东医疗";
    
    select count(link) from eastmoney_carticle where code = 'GQY视讯' and article is NULL;
    select count(1) from  eastmoney_carticle where article is not NULL;
    """
