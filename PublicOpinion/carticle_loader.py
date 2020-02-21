# -*- coding: utf-8 -*-
import json
import logging
import random
import re
import string
import time
import traceback
from urllib.parse import urlencode

import pymysql
import requests
from lxml import html
import sys

sys.path.append("./../")
from PublicOpinion.configs import MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, DC_HOST, DC_PORT, \
    DC_USER, DC_PASSWD, DC_DB, LOCAL, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, \
    LOCAL_MYSQL_DB
from PublicOpinion.sql_pool import PyMysqlPoolBase


logger = logging.getLogger()


class CArticle(object):
    def __init__(self, key):
        # 本地运行亦或者是在服务器上运行
        self.local = LOCAL
        # 是否使用阿布云代理
        self.abu = False
        # 股票代码中文简称
        self.key = key
        self.start_url = 'http://api.so.eastmoney.com/bussiness/Web/GetSearchList?'
        self.page_size = 10
        self.headers = {
            "Referer": "http://so.eastmoney.com/CArticle/s?keyword={}".format(self.key.encode()),
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",


        }
        self.db = MYSQL_DB
        self.table = "eastmoney_carticle"
        if self.local:
            conf = {
                "host": LOCAL_MYSQL_HOST,
                "port": LOCAL_MYSQL_PORT,
                "user": LOCAL_MYSQL_USER,
                "password": LOCAL_MYSQL_PASSWORD,
                "db": LOCAL_MYSQL_DB,
            }
        else:
            conf = {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
                "db": MYSQL_DB,
            }
        self.sql_pool = PyMysqlPoolBase(**conf)
        # 不使用阿布云的情况下 初始化代理
        if not self.abu:
            self.proxy = self._get_proxy()
        # 记录出错的列表页 以及 详情页 url
        self.error_detail = []
        self.error_list = []

    def make_query_params(self, msg, page):
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

    def contract_sql(self, to_insert):
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
            insert_sql, values = self.contract_sql(to_insert)
            count = self.sql_pool.insert(insert_sql, values)
        except pymysql.err.IntegrityError:
            logger.warning("重复 ")
        except:
            logger.warning("失败")
        else:
            return count

    def _abu_get(self, url):
        """使用阿布云代理 默认失败后重新发起请求"""
        proxy_host = "http-cla.abuyun.com"
        proxy_port = 9030
        # 代理隧道验证信息
        proxy_user = "H74JU520TZ0I2SFC"
        proxy_pass = "7F5B56602A1E53B2"
        proxy_meta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxy_host,
            "port": proxy_port,
            "user": proxy_user,
            "pass": proxy_pass,
        }
        proxies = {
            "http": proxy_meta,
            "https": proxy_meta,
        }
        retry = 2  # 重试三次 事不过三^_^
        while True:
            try:
                resp = requests.get(url,
                                    proxies=proxies,
                                    headers=self.headers,
                                    timeout=3,
                                    )
                if resp.status_code == 200:
                    return resp
                else:
                    print(resp.status_code, "retry")
                    retry -= 1
                    if retry <= 0:
                        return None
                    time.sleep(3)
            except:
                print("error retry")
                retry -= 1
                if retry <= 0:
                    return None
                time.sleep(3)

    def _get_proxy(self):
        if self.local:
            r = requests.get('http://192.168.0.102:8888/get')
        else:
            r = requests.get('http://172.17.0.4:8888/get')
        proxy = r.text
        return proxy

    def _crawl(self, url, proxy):
        proxies = {'http': proxy}
        r = requests.get(url, proxies=proxies, headers=self.headers, timeout=3)
        return r

    def _get(self, url):
        if self.abu:
            return self._abu_get(url)

        count = 0
        while True:
            count = count + 1
            try:
                resp = self._crawl(url, self.proxy)
                if resp.status_code == 200:
                    return resp
                elif count > 2:
                    logger.warning(f'抓取网页{url}最终失败')
                    break
                else:
                    self.proxy = self._get_proxy()
                    logger.warning(f"无效状态码{resp.status_code}, 更换代理{self.proxy}\n")
            except:
                self.proxy = self._get_proxy()
                logger.warning(f'代理失败,更换代理{self.proxy} \n')

    def _parse_detail(self, detail_page):
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

    def _select_key_links(self):
        select_all_sql = f"select link from {self.table} where code = '{self.key}' and article is NULL;"
        # links = self.sql_pool.select_many(select_all_sql, size=10)
        links = self.sql_pool.select_all(select_all_sql)
        return links

    def _select_rest_all_links(self):
        select_all_sql = f"select link from {self.table} where article is NULL;"
        links = self.sql_pool.select_many(select_all_sql, size=20)
        # links = self.sql_pool.select_all(select_all_sql)
        return links

    def transferContent(self, content):
        if content is None:
            return None
        else:
            string = ""
            for c in content:
                if c == '"':
                    string += '\\\"'
                elif c == "'":
                    string += "\\\'"
                elif c == "\\":
                    string += "\\\\"
                else:
                    string += c
            return string

    def _filter_char(self, test_str):
        # 处理特殊的空白字符
        # '\u200b' 是 \xe2\x80\x8b
        for cha in ['\n', '\r', '\t',
                    '\u200a', '\u200b', '\u200c', '\u200d', '\u200e',
                    '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
                    ]:
            test_str = test_str.replace(cha, '')
        test_str = test_str.replace(u'\xa0', u' ')  # 把 \xa0 替换成普通的空格
        return test_str

    def _process_content(self, vs):
        # 去除 4 字节的 utf-8 字符，否则插入mysql时会出错
        try:
            # python UCS-4 build的处理方式
            highpoints = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            # python UCS-2 build的处理方式
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

        params = list()
        for v in vs:
            # 对插入数据进行一些处理
            nv = highpoints.sub(u'', v)
            nv = self._filter_char(nv)
            params.append(nv)
        return "".join(params)

    def _update_detail(self, link, article):
        # 直接插入文本内容可能出错 需对其进行处理
        # article = self.transferContent(article)
        article = self._process_content(article)
        print("文章内容是: \n", article)
        update_sql = f"update {self.table} set article =%s where link =%s;"
        try:
            ret = self.sql_pool.update(update_sql, [(article), (link)])
            # ret = self.sql_pool.update(update_sql)
        except:
            traceback.print_exc()
            print("插入失败")
            return None
        else:
            return ret

    def _get_list(self, list_url):
        resp = self._get(list_url)
        if resp:
            return resp.text
        else:
            self.error_list.append(list_url)

    def _get_detail(self, detail_url):
        resp = self._get(detail_url)
        if resp:
            return resp.text
        else:
            self.error_detail.append(detail_url)

    def _parse_list(self, list_page):
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

    def _save_one_page_list(self, page):
        list_url = self.start_url + urlencode(self.make_query_params(self.key, page))
        list_page = self._get_list(list_url)
        if list_page:
            list_infos = self._parse_list(list_page)  # list
            if not list_infos:
                logger.info(f"{self.key} 爬取完毕 ")
                return

            for data in list_infos:
                item = dict()
                item['code'] = self.key
                link = data.get("ArticleUrl")
                item['link'] = link
                item['title'] = data.get("Title")
                item['pub_date'] = data.get("ShowTime")
                print("item", item)
                ret = self._save(item)
                if not ret:
                    logger.warning(f"插入失败 {item}")
            self.sql_pool.end()  # self.sql_pool.connection.commit()
            print(f"第{page}页保存成功")
            return page

    def __del__(self):
        try:
            self.sql_pool.dispose()
        except:
            pass


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

    def _start_instance(self, key):
        c = CArticle(key)
        now = lambda: time.time()
        t1 = now()
        cur = t1
        for page in range(1, 50000):
            page = c._save_one_page_list(page)
            if not page:
                break
            print(f"第 {page} 页, 累计用时 {now() - t1}, 当前页用用时 {now() - cur} ")
            cur = now()
        c.sql_pool.dispose()
        with open("record.txt", "a+") as f:
            f.write(f"{key}: error_list: {c.error_list}, error_detail: {c.error_detail}\r\n")

    def run_list(self, start=None, end=None, key=None):
        if key:
            self._start_instance(key)
        else:
            for key in self.keys[start: end]:
                self._start_instance(key)

    def _start_rest_detail(self):
        c = CArticle("")
        while True:
            links = c._select_rest_all_links()
            if len(links) < 20:
                break
            print(links)
            print("length:", len(links))
            for link in links:
                link = link.get("link")
                detail_resp = c._get(link)
                print("resp:", detail_resp)
                if detail_resp:
                    detail_page = detail_resp.text
                    article = c._parse_detail(detail_page)
                    # print("article: ", article)
                    ret = c._update_detail(link, article)
                    if ret:
                        print("更新成功")
                    else:
                        print("更新失败")
            print("一次提交")
            c.sql_pool.end()

    def _start_ins_detail(self, key):
        c = CArticle(key)
        links = c._select_key_links()
        print(links)
        count = 0
        for link in links:
            link = link.get("link")
            print("当前处理连接:", link)
            detail_resp = c._get(link)
            print("响应结果: ", detail_resp)
            if detail_resp:
                detail_page = detail_resp.text
                article = c._parse_detail(detail_page)
                ret = c._update_detail(link, article)
                if ret:
                    print("更新成功")
                else:
                    print("更新失败")
                count += 1
                if count > 9:
                    print("提交")
                    c.sql_pool.end()
                    count = 0
        c.sql_pool.dispose()

    def run_detail(self, start=None, end=None, key=None):
        if key:
            self._start_ins_detail(key)
        else:
            for k in self.keys[start: end]:
                print(k)
                self._start_ins_detail(k)


if __name__ == "__main__":
    s = Schedule()
    print(s.keys)
    print(s.keys.index('太平洋'))
    # 0
    # '中国软件', '中国通号', '中国重工', '中国重汽', '中国铁建', '中国铝业', '中国银河', '中国银行', '中国长城',
    # '中国高科', '中坚科技', '中基健康', '中大力德', '中天科技', '中天能源', '中天金融', '中威电子', '中孚信息',
    # '中孚实业', '中安科', '中宠股份', '中密控股', '中富通', '中山公用', '中山金马', '中川国际', '中工国际',
    # '中广天择', '中广核技', '中建环能', '中弘股份', '中微公司', '中恒电气', '中恒集团', '中成股份', '中房股份',
    # '中持股份', '中捷资源', '中文传媒', '中文在线', '中新科技', '中新药业', '中新赛克', '中新集团', '中旗股份',
    # '中昌数据', '中曼石油', '中材国际', '中材科技', '中材节能', '中来股份', '中核苏阀', '中核钛白', '中欣氟材',
    # '中毅达', '中水渔业', '中油工程', '中油资本', '中油龙昌', '中泰化学', '中泰股份', '中洲控股', '中海油服',
    # '中海达', '中润资源', '中源协和', '中源家居', '中潜股份', '中炬高新', '中煤能源', '中牧股份', '中环环保',
    # '中环股份', '中环装备', '中珠医疗', '中电兴发', '中电环保', '中电电机', '中百集团', '中直股份', '中石科技',
    # '中矿资源', '中科三环', '中科云网', '中科信息', '中科创达', '中科新材', '中科曙光', '中科海讯', '中科电气',
    # '中科软', '中科金财', '中简科技', '中粮控股', '中粮科技', '中粮糖业', '中联重科', '中能电气', '中航三鑫',
    # '中航光电', '中航机电', '中航沈飞', '中航电子', '中航电测', '中航资本', '中航重机', '中航飞机', '中航高科',
    # '中船科技', '中船防务', '中色股份', '中葡股份', '中衡设计', '中装建设', '中西药业', '中视传媒', '中设集团',
    # '中超控股', '中路股份', '中远海发', '中远海控', '中远海特', '中远海科', '中远海能', '中迪投资', '中通国脉',
    # '中通客车', '中金岭南', '中金环境', '中金黄金', '中钢国际', '中钢天源', '中钨高新', '中铁工业', '中铝国际',
    # '中银绒业', '中银证券', '中闽能源', '中际旭创', '中集集团', '中青宝', '中青旅', '中顺洁柔', '中颖电子',
    # '中飞股份', '中马传动', '中鼎股份', '丰乐种业', '丰元股份', '丰华股份', '丰原药业', '丰山集团', '丰林集团',
    # '丸美股份', '丹化科技', '丹邦科技', '丽岛新材', '丽江旅游', '丽珠集团', '丽鹏股份', '久之洋', '久其软件',
    # '久吾高科', '久日新材', '久立特材', '久远银海', '久量股份', '乐凯新材', '乐凯胶片', '乐山电力', '乐心医疗',
    # '乐惠国际', '乐普医疗', '乐歌股份', '乐视网', '乐通股份', '乐鑫科技', '乔治白', '九典制药', '九华旅游', '九安医疗', '九州通', '九强生物', '九有股份', '九洲电气', '九洲药业', '九牧王', '九芝堂', '九阳股份', '九鼎新材', '乾景园林', '乾照光电', '二三四五', '二六三', '二局股份', '二重重装', '云内动力', '云南城投', '云南旅游', '云南白药', '云南能投', '云南铜业', '云南锗业', '云图控股', '云大科技', '云天化', '云意电气', '云投生态', '云海金属', '云煤能源', '云维股份', '云赛智联', '云铝股份', '五方光电', '五洋停车', '五洲交通', '五洲新春', '五矿发展', '五矿稀土', '五矿资本', '五粮液', '亚世光电', '亚光股份', '亚厦股份', '亚士创能', '亚太实业', '亚太科技', '亚太股份', '亚太药业', '亚威股份', '亚宝药业', '亚振家居', '亚星化学', '亚星客车', '亚星锚链', '亚普股份', '亚泰国际', '亚泰集团', '亚玛顿', '亚盛集团', '亚翔集成', '亚联发展', '亚通股份', '亚邦股份', '交大昂立', '交建股份', '交控科技', '交运股份', '交通银行', '亨通光电', '京东方', '京华激光', '京城股份', '京天利', '京威股份', '京山轻机', '京投发展', '京新药业', '京汉股份', '京沪高铁', '京泉华', '京粮控股', '京能电力', '京能置业', '京蓝科技', '京运通', '人人乐', '人民同泰', '人民网', '人福医药', '亿利洁能', '亿利达', '亿嘉和', '亿帆医药', '亿晶光电', '亿纬锂能', '亿联网络', '亿通科技', '亿阳信通', '仁东控股', '仁和药业', '仁智股份', '今世缘', '今创集团', '今天国际', '今飞凯达', '仙乐健康', '仙坛股份', '仙琚制药', '仙鹤股份', '仟源医药',

    # 600
    # '以岭药业', '仰帆控股', '任子行', '伊之密', '伊利股份', '伊力特', '伊戈尔', '众业达', '众信旅游', '众兴菌业', '众合科技', '众和股份', '众应互联', '众泰汽车', '众源新材', '众生药业', '优刻得', '优博讯', '优德精密', '会畅通讯', '会稽山', '伟明环保', '伟星新材', '伟星股份', '伟隆股份', '传化智联', '传艺科技', '传音控股', '伯特利', '佐力药业', '佛塑科技', '佛山照明', '佛慈制药', '佛燃股份', '佩蒂股份', '佰仁医疗', '佳云科技', '佳创视讯', '佳力图', '佳发教育', '佳士科技', '佳沃股份', '佳电股份', '佳禾智能', '佳纸股份', '佳讯飞鸿', '佳通轮胎', '佳都科技', '佳隆股份', '供销大集', '依米康', '依顿电子', '侨源气体', '侨银环保', '保利发展', '保利联合', '保千里', '保变电气', '保税科技', '保隆科技', '保龄宝', '信威集团', '信息发展', '信捷电气', '信立泰', '信维通信', '信达地产', '信邦制药', '信隆健康', '信雅达', '倍加洁', '值得买', '健友股份', '健帆生物', '健康元', '健民集团', '健盛集团', '傲农生物', '元利科技', '元力股份', '元成股份', '元祖股份', '元隆雅图', '兄弟科技', '兆丰股份', '兆新股份', '兆日科技', '兆易创新', '兆驰股份', '先导智能', '先河环保', '先达股份', '先进数通', '先锋新材', '先锋电子', '光一科技', '光力科技', '光华科技', '光启技术', '光大嘉宝', '光大证券', '光大银行', '光威复材', '光峰科技', '光库科技', '光弘科技', '光明乳业', '光明地产', '光正集团', '光洋股份', '光环新网', '光电股份', '光线传媒', '光莆股份', '光迅科技', '光韵达', '克劳斯', '克明面业', '克来机电', '兔宝宝', '兖州煤业', '全信股份', '全志科技', '全新好', '全柴动力', '全筑股份', '全聚德', '全通教育', '八一钢铁', '八亿时空', '八方股份', '八菱科技', '公牛集团', '六国化工', '兰太实业', '兰州民百', '兰州铝业', '兰州黄河', '兰生股份', '兰石重装', '兰花科创', '共达电声', '共进股份', '兴业矿业', '兴业科技', '兴业股份', '兴业证券', '兴业银行', '兴化股份', '兴发集团', '兴图新科', '兴森快捷', '兴民智通', '兴源环境', '兴瑞科技', '兴蓉环境', '兴齐眼药', '养元饮品', '冀东水泥', '冀东装备', '冀中能源', '冀凯股份', '内蒙一机', '内蒙华电', '再升科技', '农业银行', '农产品', '农发种业', '农尚环境', '冠农股份', '冠城大通', '冠昊生物', '冠福股份', '冠豪高新', '冰川网络', '冰轮环境', '准油股份', '凌云股份', '凌钢股份', '凌霄泵业', '凤凰传媒', '凤凰光学', '凤凰股份', '凤形股份', '凤竹纺织', '凯中精密', '凯乐科技', '凯众股份', '凯伦股份', '凯利泰', '凯发电气', '凯恩股份', '凯撒文化', '凯撒股份', '凯文教育', '凯普生物', '凯瑞德', '凯盛科技', '凯美特气', '凯莱英', '凯迪生态', '凯龙股份', '出版传媒', '分众传媒', '刚泰控股', '创业慧康', '创业环保', '创业黑马', '创元科技', '创兴资源', '创力集团', '创意信息', '创新医疗', '创智信息', '创源文化', '创维数字', '初灵信息', '利亚德', '利君股份', '利安隆', '利尔化学', '利德曼', '利欧股份', '利民股份', '利源精制', '利群股份', '利通电子', '剑桥科技', '力合科技', '力帆股份', '力星股份', '力源信息', '力生制药', '力盛赛车', '加加食品', '动力源', '劲嘉股份', '劲拓股份', '劲胜智能', '勘设股份', '勤上股份', '包头铝业', '包钢股份', '北京利尔', '北京君正', '北京城乡', '北京城建', '北京文化', '北京科锐', '北京银行', '北信源', '北化股份', '北大医药', '北大科技', '北大荒', '北巴传媒', '北斗星通', '北新建材', '北新路桥', '北方五环', '北方华创', '北方国际', '北方导航', '北方稀土', '北方股份', '北特科技', '北玻股份', '北矿科技', '北纬科技', '北讯集团', '北辰实业', '北部湾港', '北陆药业', '千山药机', '千方科技', '千禾味业', '千红制药', '千金药业', '升达林业', '华业资本', '华东医药', '华东数控', '华东电脑', '华东科技', '华东重机', '华中数控', '华丽家族', '华仁药业', '华仪电气', '华伍股份', '华体科技', '华侨城', '华信国际', '华信新材', '华信股份', '华光股份', '华兰生物', '华兴源创', '华凯创意', '华创阳安', '华力创通', '华北制药', '华北高速', '华升股份', '华友钴业', '华发股份', '华圣科技', '华域汽车', '华培动力', '华塑控股', '华夏幸福', '华夏航空', '华夏银行', '华大基因', '华天科技', '华天酒店', '华媒控股', '华孚时尚', '华宇软件', '华安证券', '华宏科技', '华宝香精', '华峰氨纶', '华峰测控', '华峰超纤', '华工科技', '华帝股份', '华平股份', '华建集团', '华录百纳', '华微电子', '华懋科技', '华扬联众', '华控赛格', '华数传媒', '华斯股份', '华新水泥', '华昌化工', '华昌达', '华明装备', '华星创业', '华映科技', '华林证券', '华森制药', '华正新材', '华泰股份', '华泰证券', '华泽钴镍', '华测导航', '华测检测', '华海药业', '华润三九', '华润双鹤', '华润微', '华源控股', '华灿光电', '华熙生物', '华特气体', '华瑞股份', '华电国际', '华电能源', '华电重工', '华立股份', '华策影视', '华纺股份', '华统股份', '华联商厦', '华联控股', '华联综超', '华联股份', '华胜天成', '华能国际', '华能水电', '华脉科技', '华自科技', '华致酒行', '华英农业', '华茂股份', '华荣股份', '华菱星马', '华菱精工', '华菱钢铁', '华虹计通', '华西股份', '华西能源', '华西证券', '华讯方舟', '华谊兄弟', '华谊嘉信', '华谊集团', '华贸物流', '华资实业', '华软科技', '华辰装备', '华达科技', '华远地产', '华通医药', '华通热力', '华邦健康', '华金资本',



    # 1000
    # '太平洋', '太平鸟', '太极实业', '太极股份', '太极集团', '太空智造', '太行水泥', '太辰光', '太钢不锈', '太阳电缆', '太阳纸业', '太阳能', '太龙照明', '太龙药业', '奇信股份', '奇正藏药', '奇精机械', '奋达科技', '奥佳华', '奥克股份', '奥士康', '奥康国际', '奥拓电子', '奥普光电', '奥普家居', '奥特佳', '奥特迅', '奥瑞德', '奥瑞金', '奥福环保', '奥维通信', '奥美医疗', '奥翔药业', '奥联电子', '奥赛康', '奥赛康', '奥飞娱乐', '奥飞数据', '奥马电器', '好利来', '好太太', '好当家', '好想你', '好莱客', '如意集团', '如通股份', '妙可蓝多', '姚记科技', '威创股份', '威华股份', '威唐工业', '威孚高科', '威尔泰', '威尔药业', '威帝股份', '威星智能', '威派格', '威海广泰', '威胜信息', '威龙股份', '孚日股份', '宁夏建材', '宁德时代', '宁沪高速', '宁波东力', '宁波中百', '宁波华翔', '宁波富达', '宁波富邦', '宁波建工', '宁波水表', '宁波海运', '宁波港', '宁波热电', '宁波精达', '宁波联合', '宁波银行', '宁波韵升', '宁波高发', '宇信科技', '宇晶股份', '宇环数控', '宇瞳光学', '宇通客车', '宇顺电子', '安井食品', '安信信托', '安凯客车', '安利股份', '安博通', '安图生物', '安奈儿', '安妮股份', '安居宝', '安彩高科', '安德利', '安徽合力', '安徽建工', '安恒信息', '安控科技', '安正时尚', '安泰科技', '安泰集团', '安洁科技', '安源煤业', '安琪酵母', '安硕信息', '安科瑞', '安科生物', '安纳达', '安记食品', '安诺其', '安车检测', '安达维尔', '安迪苏', '安通控股', '安道麦', '安阳钢铁', '安集科技', '安靠智电', '宋城演艺', '宋都股份', '完美世界', '宏创控股', '宏发股份', '宏和科技', '宏图高科', '宏大爆破', '宏川智慧', '宏昌电子', '宏润建设', '宏源证券', '宏盛科技', '宏盛股份', '宏良股份', '宏辉果蔬', '宏达新材', '宏达电子', '宏达矿业', '宏达股份', '宏达高科', '宗申动力', '宜华健康', '宜华生活', '宜安科技', '宜宾纸业', '宜昌交运', '宜通世纪', '宝丰能源', '宝信软件', '宝光股份', '宝兰德', '宝利国际', '宝塔实业', '宝德股份', '宝新能源', '宝泰隆', '宝胜股份', '宝色股份', '宝莫股份', '宝莱特', '宝通科技', '宝钛股份', '宝钢包装', '宝钢股份', '宝馨科技', '宝鹰股份', '宝鼎科技', '实丰文化', '实达集团', '宣亚国际', '家家悦', '容大感光', '容百科技', '密尔克卫', '富临精工', '富临运业', '富奥股份', '富安娜', '富控互动', '富春环保', '富春股份', '富森美', '富满电子', '富瀚微', '富煌钢构', '富瑞特装', '富祥股份', '富通鑫茂', '富邦股份', '寒锐钴业', '寿仙谷', '小商品城', '小天鹅', '小康股份', '小熊电器', '尔康制药', '尖峰集团', '尚品宅配', '尚纬股份', '尚荣医疗', '尤夫股份', '居然之家', '展鹏科技', '山东出版', '山东华鹏', '山东地矿', '山东墨龙', '山东威达', '山东海化', '山东矿机', '山东章鼓', '山东药玻', '山东赫达', '山东路桥', '山东钢铁', '山东铝业', '山东高速', '山东黄金', '山大华特', '山推股份', '山水文化', '山河智能', '山河药辅', '山煤国际', '山石网科', '山西汾酒', '山西焦化', '山西证券', '山西路桥', '山鹰控股', '山鼎设计', '岭南控股', '岭南股份', '岱勒新材', '岱美股份', '岳阳兴长', '岳阳林纸', '岷江水电', '峨眉旅游', '崇达技术', '川仪股份', '川大智胜', '川恒股份', '川投能源', '川润股份', '川环科技', '川能动力', '川金诺', '工业富联', '工商银行', '工大高新', '左江科技', '巨人网络', '巨力索具', '巨化股份', '巨星科技', '巨轮智能', '巴士在线', '巴安水务', '市北高新', '希努尔', '帝尔激光', '帝欧家居', '常宝股份', '常山北明', '常山药业', '常柴股份', '常熟汽饰', '常熟银行', '常铝股份', '常青股份', '平安银行', '平庄能源', '平治信息', '平潭发展', '平煤股份', '平高电气', '幸福蓝海', '广东明珠', '广东榕泰', '广东甘化', '广东金曼', '广东骏亚', '广东鸿图', '广信材料', '广信股份', '广博股份', '广发证券', '广和通', '广哈通信', '广大特材', '广宇发展', '广宇集团', '广安爱众', '广州发展', '广州浪奇', '广州港', '广州酒家', '广弘控股', '广日股份', '广晟有色', '广汇汽车', '广汇物流', '广汇能源', '广汽长丰', '广汽集团', '广济药业', '广深铁路', '广生堂', '广田集团', '广电电气', '广电网络', '广电计量', '广电运通', '广百股份', '广联达', '广聚能源', '广西广电', '广誉远', '庄园牧场', '应流股份', '庞大集团', '康佳集团', '康力电梯', '康尼机电', '康弘药业', '康强电子', '康得新', '康德莱', '康恩贝', '康惠制药', '康拓红外', '康斯特', '康普顿', '康欣新材', '康泰生物', '康盛股份', '康缘药业', '康美药业', '康芝药业', '康跃科技', '康辰药业', '康达尔', '康达新材', '康隆达', '康龙化成', '廊坊发展', '延华智能', '延安必康', '延江股份', '延长化建', '建业股份', '建发股份', '建投能源', '建新股份', '建研院', '建科院', '建艺集团', '建设机械', '建设银行', '建龙微纳', '开元仪器', '开创国际', '开尔新材', '开山股份', '开开实业', '开润股份', '开滦股份', '开立医疗', '开能健康', '引力传媒', '弘业股份', '弘亚数控', '弘信电子', '弘宇股份', '弘讯科技', '弘高创意', '张家港行', '张旅集团', '张江高科', '张裕', '强力新材', '强生控股', '当代东方', '当代明诚', '当升科技', '当虹科技', '彤程新材', '彩虹股份', '彩讯股份', '徐家汇', '徐工机械', '徕木股份', '得利斯', '得润电子', '得邦照明', '御家汇', '御银股份', '微光股份', '微芯生物', '德创环保', '德力股份', '德奥通航', '德威新材', '德宏股份', '德尔未来', '德尔股份', '德展健康', '德恩精工', '德新交运', '德方纳米', '德生科技', '德美化工', '德联集团', '德艺文创', '德豪润达', '德赛电池', '德赛西威', '德邦股份', '心脉医疗', '必创科技', '志邦股份', '快克股份', '快意电梯', '思创医惠', '思源电气', '思特奇', '思维列控', '思美传媒', '怡亚通', '怡球资源', '怡达股份', '恒丰纸业', '恒为科技', '恒久科技', '恒信东方', '恒力股份', '恒华科技', '恒基达鑫', '恒大高新', '恒天海龙', '恒宝股份', '恒实科技', '恒康医疗', '恒星科技', '恒林股份', '恒泰艾普', '恒润重工', '恒源煤电', '恒瑞医药', '恒生电子', '恒立实业', '恒立液压', '恒运集团', '恒通物流', '恒通科技', '恒逸石化', '恒邦股份', '恒铭达', '恒银金融', '恒锋信息', '恒锋工具', '恒顺醋业', '恩华药业', '恩捷股份', '恺英网络', '悦心健康', '悦达投资', '惠伦晶体', '惠博普', '惠发股份', '惠城环保', '惠天热电', '惠威科技', '惠泉啤酒', '惠程科技', '惠而浦', '惠达卫浴', '意华股份', '慈文传媒', '慈星股份', '慈铭体检', '慧金科技', '成城股份', '成都燃气', '成都路桥', '成都银行', '成飞集成', '我乐家居', '我武生物', '我爱我家', '戴维医疗', '扬农化工', '扬子新材', '扬子石化', '扬帆新材', '扬杰科技', '承德钒钛', '承德露露', '抚顺特钢', '报喜鸟', '拉卡拉', '拉夏贝尔', '拉芳家化', '拓尔思', '拓斯达', '拓日新能', '拓普集团', '拓维信息', '拓邦股份', '招商公路', '招商南油', '招商地产', '招商港口', '招商积余', '招商蛇口', '招商证券',
    #
    #
    #  2000
    # over...

    sys.exit(0)
    # s.run_list(key="格力电器")

    import os
    key = os.environ.get("KEY", "格力电器")
    start = os.environ.get("START", 0)
    end = os.environ.get("END", 0)
    print(key, start, end)
    s.run_detail(key=key, start=int(start), end=int(end))
