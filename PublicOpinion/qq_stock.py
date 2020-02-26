import json
import logging
import time
import pymysql
import requests
from gne import GeneralNewsExtractor
from requests.exceptions import ProxyError, Timeout, ConnectionError, ChunkedEncodingError

from PublicOpinion.configs import LOCAL, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL_MYSQL_HOST, \
    LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, LOCAL_MYSQL_DB
from PublicOpinion.sql_pool import PyMysqlPoolBase

logger = logging.getLogger()


class qqStock(object):
    def __init__(self):
        self.local = LOCAL
        self.token = "8f6b50e1667f130c10f981309e1d8200"
        self.headers = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 "
                                      "(KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"}
        self.list_url = "https://pacaio.match.qq.com/irs/rcd?cid=52&token={}" \
       "&ext=3911,3922,3923,3914,3913,3930,3915,3918,3908&callback=__jp1".format(self.token)
        # self.proxy = None
        self.extractor = GeneralNewsExtractor()

        self.local = LOCAL
        if self.local:
            conf = {
                "host": LOCAL_MYSQL_HOST,
                "port": LOCAL_MYSQL_PORT,
                "user": LOCAL_MYSQL_USER,
                "password": LOCAL_MYSQL_PASSWORD,
                "db": LOCAL_MYSQL_DB,

            }
            self.db = LOCAL_MYSQL_DB
        else:
            conf = {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
                "db": MYSQL_DB,
            }
            self.db = MYSQL_DB

        self.sql_pool = PyMysqlPoolBase(**conf)
        self.table = "qq_Astock_news"
        self.error_detail = []

    # def _get_proxy(self):
    #     if self.local:
    #         proxy_url = "http://192.168.0.102:8888/get"
    #     else:
    #         proxy_url = "http://172.17.0.5:8888/get"
    #     r = requests.get(proxy_url)
    #     proxy = r.text
    #     return proxy

    def _crawl(self, url):
        r = requests.get(url, headers=self.headers, timeout=3)
        return r

        # proxies = {'http': proxy}
        # r = requests.get(url, proxies=proxies, headers=self.headers, timeout=3)
        # return r

    def _get(self, url):
        count = 0
        while True:
            count = count + 1
            try:
                resp = self._crawl(url)
                if resp.status_code == 200:
                    return resp
                elif count > 2:
                    break
                # else:
                #     self.proxy = self._get_proxy()
                #     print(f"无效状态码{resp.status_code}, 更换代理{self.proxy}\n")
            except (ChunkedEncodingError, ConnectionError, Timeout, UnboundLocalError, UnicodeError, ProxyError):
                # self.proxy = self._get_proxy()
                # print(f'代理连接失败,更换代理{self.proxy}\n')
                if count > 2:
                    break

        print(f'抓取网页{url}最终失败')

    def _parse_article(self, vurl):
        detail_page = self._get(vurl)
        if detail_page:
            result = self.extractor.extract(detail_page.text)
            return result.get("content")

    def _parse_list(self):
        list_resp = self._get(self.list_url)
        if list_resp:
            print("请求主列表页成功 ")
            body = list_resp.text
            body = body.lstrip("__jp1(")
            body = body.rstrip(")")
            body = json.loads(body)
            datas = body.get("data")

            specials = []
            articles = []

            for data in datas:
                if data.get("article_type") == 120:
                    specials.append(data)
                elif data.get("article_type") == 0:
                    articles.append(data)
                else:
                    print("爬取到预期外的数据{}".format(data))
                    print("爬取到预期外的数据类型{}".format(data.get("article_type")))  # 56 视频类型 不再爬取

            return specials, articles

    def _contract_sql(self, to_insert):
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

    def _save(self, to_insert):
        try:
            insert_sql, values = self._contract_sql(to_insert)
            count = self.sql_pool.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            # logger.warning("重复")
            return 1
        except:
            logger.warning("失败")
        else:
            return count

    def _start(self):
        specials, articles = self._parse_list()
        for article in articles:
            item = {}
            vurl = article.get("vurl")
            item['link'] = vurl
            item['pub_date'] = article.get("publish_time")
            item['title'] = article.get("title")
            article = self._parse_article(vurl)
            if article:
                item['article'] = article
                # print(item)
                ret = self._save(item)
                if not ret:
                    print('保存失败')
                    self.error_detail.append(vurl)
            else:
                self.error_detail.append(vurl)

        print("开始处理专题页")

        for special in specials:
            special_id = special.get("app_id")
            special_url = "https://pacaio.match.qq.com/openapi/getQQNewsSpecialListItems?id={}&callback=getSpecialNews".format(special_id)
            ret = self._get(special_url).text
            ret = ret.lstrip("""('getSpecialNews(""")
            ret = ret.rstrip(""")')""")
            jsonobj = json.loads(ret)
            # print(jsonobj)

            data = jsonobj.get("data")
            id_list = data.get("idlist")
            for one in id_list:
                new_list = one.get('newslist')
                for new in new_list:
                    # print("标题:", new.get("longtitle"), end=",")
                    # # print("链接:", new.get("surl"), end=",")
                    # # "https://new.qq.com/omn/{}/{}.html".format(id[:6], id)
                    # id = new.get("id")
                    # print("链接:", "https://new.qq.com/omn/{}/{}.html".format(id[:8], id), end=",")
                    # print("发布时间:", new.get("time"))
                    item = {}
                    id = new.get("id")
                    link = "https://new.qq.com/omn/{}/{}.html".format(id[:8], id)
                    title = new.get("longtitle")
                    pub_date = new.get("time")
                    if link and title and pub_date:
                        article = self._parse_article(link)
                        if article:
                            item['link'] = link
                            item['pub_date'] = pub_date
                            item['title'] = title
                            item['article'] = article
                            # print(item)
                            ret = self._save(item)
                            if not ret:
                                print("保存失败")
                                self.error_detail.append(link)
                        else:
                            self.error_detail.append(link)

    def __del__(self):
        self.sql_pool.dispose()


if __name__ == "__main__":
    now = lambda: time.time()
    t1 = now()
    d = qqStock()
    d._start()
