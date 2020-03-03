# coding=utf8
import datetime
import random
import re
import time
import traceback

import pymysql
import requests
from gne import GeneralNewsExtractor
from lxml import html

from PublicOpinion.configs import LOCAL, LOCAL_MYSQL_HOST, LOCAL_MYSQL_PORT, LOCAL_MYSQL_USER, LOCAL_MYSQL_PASSWORD, \
    LOCAL_MYSQL_DB, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, LOCAL_PROXY_URL, PROXY_URL
from PublicOpinion.sql_pool import PyMysqlPoolBase


class Base(object):
    def __init__(self):
        self.local = LOCAL
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/79.0.3945.117 Safari/537.36'
        }
        self.use_proxy = 0

    def _init_pool(self):
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

    def _get_proxy(self):
        if self.local:
            return requests.get(LOCAL_PROXY_URL).text.strip()
        else:
            random_num = random.randint(0, 10)
            if random_num % 2:
                time.sleep(1)
                return requests.get(PROXY_URL).text.strip()
            else:
                return requests.get(LOCAL_PROXY_URL).text.strip()

    def get(self, url):
        if not self.use_proxy:
            return requests.get(url, headers=self.headers)

        count = 0
        while True:
            count += 1
            if count > 10:
                return None
            try:
                proxy = {"proxy": self._get_proxy()}
                print("proxy is >> {}".format(proxy))
                resp = requests.get(url, headers=self.headers, proxies=proxy)
            except:
                traceback.print_exc()
                time.sleep(0.5)
            else:
                if resp.status_code == 200:
                    return resp
                elif resp.status_code == 404:
                    return None
                else:
                    print("status_code: >> {}".format(resp.status_code))
                    time.sleep(1)
                    pass

    def convert_dt(self, time_stamp):
        d = str(datetime.datetime.fromtimestamp(time_stamp))
        return d

    def _contract_sql(self, to_insert):
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        ks = sorted(ks)
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}` '''.format(self.table) + fields_str + ''' values ''' + values_str + ''';'''
        return base_sql

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
        content = "".join(params).strip()
        return content

    def _get_values(self, item: dict):
        # self.fields: []  插入所需字段列表 同时与上文的 ks = sorted(ks) 对应
        value = tuple(item.get(field) for field in sorted(self.fields))
        return value

    def _save(self, item):
        insert_sql = self._contract_sql(item)
        value = self._get_values(item)
        try:
            ret = self.sql_pool.insert(insert_sql, value)
        except pymysql.err.IntegrityError:
            print("重复数据 ")
            return 1
        except:
            traceback.print_exc()
        else:
            return ret

    def _save_many(self, items):
        values = [self._get_values(item) for item in items]   # list of tuple
        insert_many_sql = self._contract_sql(items[0])
        try:
            ret = self.sql_pool.insert_many(insert_many_sql, values)
        except pymysql.err.IntegrityError:
            print("批量中有重复数据")
        except:
            traceback.print_exc()
        else:
            return ret
        finally:
            self.sql_pool.end()

    def save_one(self, item):
        self._save(item)
        self.sql_pool.end()

    def save(self, items):
        if not items:
            print("批量数据为空 ")
            return
        ret = self._save_many(items)
        if not ret:
            print("批量保存失败 开始单独保存 .. ")
            count = 0
            for item in items:
                print(item)
                self._save(item)
                count += 1
                if count > 9:
                    self.sql_pool.end()
                    count = 0
            # self.sql_pool.dispose()
            self.sql_pool.end()
        else:
            print("批量成功..")
            print(items)
            print(len(items))

    def __del__(self):
        try:
            self.sql_pool.dispose()
        except:
            pass

    def start(self):
        try:
            self._init_pool()
            self._start()
        except:
            traceback.print_exc()


class Reference(Base):
    def __init__(self):
        super(Reference, self).__init__()
        self.index_url = 'http://www.jfinfo.com/reference'
        self.more_url = 'http://www.jfinfo.com/articles_categories/more?page={}&category_id=13'
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'Hm_lvt_eb1542e7fa53709d9037dcc8c652e026=1583204516; Hm_lpvt_eb1542e7fa53709d9037dcc8c652e026=1583205739; _jfinfo_session=SzdiRTlIeUw5QXdObkRSNG5kUGpVRDNCQld3NGVkcTcrWnVNR3dZdTA4TWxoRVd3VENkQlBTeHcxQkdGaS9nUG9qdDVEeFlqMEI1OFdQMmdYNXJLTyt0YzJjRkRVbEVKa25YOUQvWUl5RjZFTm5WbENuN1JLZ05RSFR4cEVYVW90alhpSGNHSldiYWlZMDNXR0NuK293PT0tLWJwd2UybVpjREltRHB1bUxMdUxBZ2c9PQ%3D%3D--4ef0e46e0b2629bbf61194ceefd60e8b6b398499',
            'Host': 'www.jfinfo.com',
            'Pragma': 'no-cache',
            'Referer': 'http://www.jfinfo.com/reference',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
            'X-CSRF-Token': '9Kgn0ZaNQJWoqIht/pDIK9h97D5wuSFQ4gbSV8eB3eeXm3BVKjz7g8kDflyf0G4LssxDAOa0J297e6x5aKPndQ==',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.extractor = GeneralNewsExtractor()
        self.table = 'jfinfo'    # 巨丰资讯
        self.fields = ['link', 'title', 'pub_date', 'article']
        self.max_page = 639

    @staticmethod
    def _process_pub_dt(pub_date: str, year: None):
        # 对 pub_date 的各类时间格式进行统一
        current_dt = datetime.datetime.now()
        today_dt_str = current_dt.strftime("%Y-%m-%d")
        yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        after_yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        if '分钟前' in pub_date:  # eg. 43分钟前
            minutes = int(pub_date.replace('分钟前', ''))
            pub_date = (current_dt - datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
        elif "小时前" in pub_date:  # eg. 20小时前
            hours = int(pub_date.replace('小时前', ''))
            pub_date = (current_dt - datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        elif "今天" in pub_date:  # eg.今天09:33
            pub_date = pub_date.replace('今天', '')
            pub_date = " ".join([today_dt_str, pub_date])
        elif "昨天" in pub_date:  # eg. 昨天04:24
            pub_date = pub_date.replace('昨天', '')
            pub_date = " ".join([yesterday_dt_str, pub_date])
        elif '前天' in pub_date:  # eg. 前天11:33
            pub_date = pub_date.replace("前天", '')
            pub_date = " ".join([after_yesterday_dt_str, pub_date])
        else:  # eg. 02-29 04:24
            if year:   # 从 link 中获取的之前某一年的新闻
                pub_date = "{}-{}".format(year, pub_date)
            else:   # 默认是今年的新闻
                pub_date = "{}-{}".format(current_dt.year, pub_date)
        return pub_date

    def _parse_detail(self, body):
        result = self.extractor.extract(body)
        content = result.get("content")
        return content

    def _parse_index(self, index_page):
        doc = html.fromstring(index_page)
        news_list = doc.xpath("//div[@class='m-contentl left']//dl")
        # print(len(news_list))
        items = []
        for news in news_list:
            item = {}
            title = news.xpath(".//a[@class='f20']/text()")[0]
            # print(title)
            item['title'] = title
            link = news.xpath(".//a[@class='f20']/@href")[0]
            # print(link)
            item['link'] = link

            _year = None
            try:
                _year = re.findall(r"news/(\d+)/", link)[0][:4]  # 20161218
            except:
                pass

            pub_date = news.xpath(".//dd/span/text()")[0]
            # print(pub_date)
            pub_date = self._process_pub_dt(pub_date, _year)
            # print(">>> ", pub_date)
            item['pub_date'] = pub_date
            # print()
            detail_resp = self.get(link)
            if detail_resp:
                detail_page = detail_resp.text
                article = self._parse_detail(detail_page)
                item['article'] = article
                items.append(item)
                print(item)
        return items

    def _parse_more(self, more_page):
        # print(more_page)
        '''
        if(!$("#bottom_load_error").data("block")){
            $("#page_num").val("2");
            $(".m-newsYaow").append('<div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2765134\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3153843/cfb2d9fa-0cbc-4a0e-99cb-be9232aad421.jpg\" alt=\"Cfb2d9fa 0cbc 4a0e 99cb be9232aad421\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2765134\">巨·个股 | 市场规模940亿！两大核心龙头已被保险巨头看中，互联网医疗大机遇<\/a>\n      <p class=\"cGray\">字字真言的选股、操作理念；价值千金的市场热点、龙头捕捉技法！应有尽有。学会炒股、洞悉热点。捕捉龙头，一份“巨·个股”就够了！导读：互联网医疗行业景气度大大提升，产业链哪些个股受益，还有没有参与的...<\/p>\n    <\/dt>\n    <dd><i>巨丰日刊<\/i><span>昨天15:30<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2764986\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3153695/b8bb5b8d-fc85-4c43-b607-a11c3960bd04.jpg\" alt=\"B8bb5b8d fc85 4c43 b607 a11c3960bd04\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2764986\">巨丰数据赢|百强席位操盘手法解密（一百四十七）：同样是打板 有些席位就要回避<\/a>\n      <p class=\"cGray\">【巨丰投顾】大数据研发团队依托四大数据库，针对市场百强龙虎榜营业部全面进行数据回测分析，帮助分析师、投资顾问、专业投资者解析各路一线游资操盘手法，助您看清对手“底牌”，数据回测告诉我们，一旦一线...<\/p>\n    <\/dt>\n    <dd><i>百强席位<\/i><span>昨天15:19<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2764983\"><img src=\"https://asset3.tougub.com/assets/default/article/cover/77-7c3d31472851be786c76384e4d30292eb77133f949a42fc573c212f8901240fc.jpg\" alt=\"77\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2764983\">巨·财经 | A股“宏观因子指标”探明底部？<\/a>\n      <p class=\"cGray\">追踪最新鲜的财经事件，探寻热点背后的投资机会。巨丰投顾“巨·财经”为您专业解读财经事件背后的投资秘密。导读：2月财新中国制造业PMI降至40.3，为有数据以来最低，A股“宏观因子指标”探明底部？...<\/p>\n    <\/dt>\n    <dd><i>巨丰日刊<\/i><span>昨天15:00<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2764979\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3153686/91349942-0a8b-48be-8eb0-f0efd797dc1b.png\" alt=\"91349942 0a8b 48be 8eb0 f0efd797dc1b\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2764979\">头号研报：中长期贷款增加 大基建投资提速带来结构性机会<\/a>\n      <p class=\"cGray\">“研报也要做头号”——巨丰投顾最新栏目“头号研报”正式上线。在众多研报之中，我们通过层层对比和筛选分析，经过提炼、加工，每周精选3-6篇有质量的文章，以“带你读研报”为目的，力争通过研报学习，挖掘市场投资机。\n<\/p>\n    <\/dt>\n    <dd><i>头号研报<\/i><span>昨天13:26<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2764261\"><img src=\"https://asset3.tougub.com/assets/default/article/cover/12-501b4dfb44d6a1942b6c9ea4df1253500c9b3b3f9f58291e4821d791a3464af8.jpg\" alt=\"12\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2764261\">巨丰投顾独家解读：非洲猪瘟疫苗创制成功<\/a>\n      <p class=\"cGray\">事件：中国农业科学院哈尔滨兽医研究所在《中国科学：生命科学》英文版在线发表研究论文，报道了一株人工缺失七个基因的非洲猪瘟弱毒活疫苗对家猪具有良好的安全性和有效性。巨丰投顾指出，非洲猪瘟疫苗创制成...<\/p>\n    <\/dt>\n    <dd><i>独家解读<\/i><span>昨天10:58<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2764260\"><img src=\"https://asset2.tougub.com/assets/default/article/cover/63-d2a497ff78220446101ea781908b645df896ec412cae8f785a4a517c5dd5cd1e.jpg\" alt=\"63\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2764260\">巨丰投顾独家解读：沪指涨逾2% 水泥等板块指数涨逾5%<\/a>\n      <p class=\"cGray\">事件：沪指涨逾2%，创业板指涨近1.2%，水泥、医废处理、建筑装饰等板块指数涨逾5%。巨丰投顾指出，基建板块大涨主要源于疫情对经济冲击之下基建稳增长预期。最新PMI数据显示2月财新制造业PMI降...<\/p>\n    <\/dt>\n    <dd><i>独家解读<\/i><span>昨天10:55<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2763710\"><img src=\"https://asset3.tougub.com/assets/default/article/cover/12-501b4dfb44d6a1942b6c9ea4df1253500c9b3b3f9f58291e4821d791a3464af8.jpg\" alt=\"12\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2763710\">巨丰投顾独家解读：2月财新中国制造业PMI40.3 为有数据以来最低 <\/a>\n      <p class=\"cGray\">事件：2月财新中国制造业PMI降至40.3 为有数据以来最低。巨丰投顾指出，各行业受影响程度存在差异，保证民生需求的农副食品加工、食品及酒饮料精制茶等行业PMI明显高于制造业整体水平。为减少疫情...<\/p>\n    <\/dt>\n    <dd><i>独家解读<\/i><span>昨天10:15<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2763709\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3152414/e1fa1fb0-8f1e-401b-96a6-4ccff235a1f8.jpg\" alt=\"E1fa1fb0 8f1e 401b 96a6 4ccff235a1f8\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2763709\">外盘头条:国际油价跌跌不休？得看OPEC出不出手<\/a>\n      <p class=\"cGray\">全球财经媒体周末共同关注的头条新闻主要有：1、特朗普政府考虑减税措施 施压美联储增加降息可能2、央行研究人员：全球经济“V”型复苏看起来“非常不现实”3、美银美林：衰退忧虑升级 投资者逃离股市转...<\/p>\n    <\/dt>\n    <dd><i>海外观察<\/i><span>昨天09:46<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2763462\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3152166/884186f3-5c1d-47ae-af01-15ff367b365d.jpg\" alt=\"884186f3 5c1d 47ae af01 15ff367b365d\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2763462\">大参考：美股半导体板块引领市场 全球半导体出货有望再超1万亿件<\/a>\n      <p class=\"cGray\">今日导读1、新证券法3月1日起正式实施。3月1日起公司债券公开发行实行注册制，沪深交易所表示，加快制定公司债券实施注册制配套规则。2、截至北京时间3月1日20时，中国以外共61个国家和地区报告新...<\/p>\n    <\/dt>\n    <dd><i>大参考<\/i><span>昨天09:21<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2763461\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3152165/7448a268-08b4-494e-9de2-dc579c2d48a5.jpg\" alt=\"7448a268 08b4 494e 9de2 dc579c2d48a5\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2763461\">巨丰数据赢｜北上资金持仓曝光 上周主力加仓个股出炉<\/a>\n      <p class=\"cGray\">北上资金增持个股数量上周五小幅回升。其中上海主板个股被北上资金减持占比最大。从板块方面看，建筑装饰和农业板块被资金小幅增持。而轻工制造和家电板块被资金减持力度较为大，需注意。 从上一周数据统计看...<\/p>\n    <\/dt>\n    <dd><i>巨丰数据赢<\/i><span>昨天09:19<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2763458\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3152161/d9d8aaf9-450b-40be-a450-5904578f2b58.jpg\" alt=\"D9d8aaf9 450b 40be a450 5904578f2b58\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2763458\">巨丰数据赢｜北上资金上周流出 主力却逆市买入这些股<\/a>\n      <p class=\"cGray\">北上资金上周五流出24.26亿元（沪深股通使用额度），昨日成交净额（买入额-卖出额）约为-51.37亿元，继续以流出为主。从沪深港股通十大活跃股表现看，被北上资金买入金额靠前的个股主要有闻泰科技...<\/p>\n    <\/dt>\n    <dd><i>巨丰数据赢<\/i><span>昨天09:14<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2763453\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3152155/a77bf6ac-3537-42e2-b439-4e635fb20bb0.jpg\" alt=\"A77bf6ac 3537 42e2 b439 4e635fb20bb0\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2763453\">金股预测早间版：8股有望开启估值修复<\/a>\n      <p class=\"cGray\">根据A股前一交易日的市场表现，以及沪深交易所的公告信息，财务报表以及市场热点等多方面内容，巨丰投顾甄选出近期市场强势热门股，以供投资者参考。公告掘金1、三夫户外（002780）：子公司收购得清纳...<\/p>\n    <\/dt>\n    <dd><i>金股早间版<\/i><span>昨天08:38<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200302/2763233\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3151933/a2ca6466-ebe7-4b02-a6bc-eb6bc3893b5b.jpg\" alt=\"A2ca6466 ebe7 4b02 a6bc eb6bc3893b5b\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200302/2763233\">巨丰早参：新证券法实施首日 “债券注册制”落地<\/a>\n      <p class=\"cGray\">巨丰今日策略巨丰投顾认为经过连续上涨，创业板春节后已经走出一波技术性牛市。政策利好以及流动性是推动市场不断上涨的主要因素。市场连续上涨后积累了大量的获利筹码，尤其是创业板短线涨幅接近30%，有调...<\/p>\n    <\/dt>\n    <dd><i>巨丰早参<\/i><span>昨天07:35<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200301/2762886\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3151586/ce4a8769-37e4-4693-ae91-c8528732b257.jpg\" alt=\"Ce4a8769 37e4 4693 ae91 c8528732b257\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200301/2762886\">财闻点金：多地加快互联网医院建设 供需两旺推动行业爆发<\/a>\n      <p class=\"cGray\">要闻精选1.国务院办公厅近日发布通知，明确在不同市场和板块分步骤实施股票公开发行注册制。相关板块/市场注册制改革正式落地前，仍继续实施核准制。2.3月1日，发改委、证监会、沪深交易所等部门均发布...<\/p>\n    <\/dt>\n    <dd><i>财闻点金<\/i><span>03-01 22:15<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200301/2762681\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3151381/8aba9c10-3af6-4374-b968-d7b1af196536.jpeg\" alt=\"8aba9c10 3af6 4374 b968 d7b1af196536\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200301/2762681\">3月1日晚间上市公司十大重磅公告<\/a>\n      <p class=\"cGray\">3月1日晚间，沪深两市多家上市公司发布重要公告：晨光生物回购资金总额上调为不低于2亿元且不超4亿元；格力电器拟注册发行债务融资工具 额度合计不超180亿元；傲农生物2月生猪销售量7.34万头 销售量环比增长77.04%。\n\n<\/p>\n    <\/dt>\n    <dd><i>晚间十大公告<\/i><span>03-01 19:03<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200229/2761494\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3150192/a3f8aee7-2933-4021-8b88-7a07aa82cf47.jpg\" alt=\"A3f8aee7 2933 4021 8b88 7a07aa82cf47\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200229/2761494\">巨丰访谈：外围市场重创 下周谁将成为人气王？<\/a>\n      <p class=\"cGray\">本周外围市场重创，A股冲高回落，而市场交投热情爆表，连续8天日成交额超万亿，下周3月开局会如何演绎？央行副行长表示对普惠金融服务达标的银行择机定向降准，定向降准对市场将产生何种影响？.........<\/p>\n    <\/dt>\n    <dd><i>巨丰访谈<\/i><span>02-29 09:04<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200228/2760430\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3149128/4f1c3c57-79d0-44bf-b473-5f7a1848ae4a.png\" alt=\"4f1c3c57 79d0 44bf b473 5f7a1848ae4a\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200228/2760430\">云丰晚报：中国经济总量逼近100万亿大关<\/a>\n      <p class=\"cGray\"><\/p>\n    <\/dt>\n    <dd><i>港股资讯<\/i><span>02-28 20:01<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200228/2760428\"><img src=\"https://asset2.tougub.com/assets/default/article/cover/51-3270b5ba9d90b46ff3c1df0e21b0cf4ca7c6e9e9a5c32580e39725a8b691bd73.jpg\" alt=\"51\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200228/2760428\">2月28日晚间上市公司十大重磅公告<\/a>\n      <p class=\"cGray\">2月28日晚间，沪深两市多家上市公司发布重要公告：万集科技受益ETC建设，2019年净利同比增逾125倍；音飞储存控股股东筹划股权转让事项，或导致公司控制权变更；新宙邦2月11日起陆续复工，目前...<\/p>\n    <\/dt>\n    <dd><i>晚间十大公告<\/i><span>02-28 19:21<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200228/2760426\"><img src=\"https://asset2.tougub.com/assets/default/article/cover/41-f71e7e8f2419e4a1b6634dfcbbd11c4b654f914a3ffa78d616bf0f48bc140e5c.jpg\" alt=\"41\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200228/2760426\">新的导火索出现！布油跌破50美元关口，欧股暴跌逾4%<\/a>\n      <p class=\"cGray\">周五午后，欧洲股市、贵金属和原油加速下跌。全球疫情升级、土俄方面的新消息都在加剧市场的恐慌情绪。CBOE恐慌指数VIX日内涨幅逾20%，与欧债危机时期相当，已高出2015和2018年抛售期间的高...<\/p>\n    <\/dt>\n    <dd><i>海外观察<\/i><span>02-28 18:15<\/span><\/dd>\n  <\/dl>\n<\/div><div class=\"slide\">\n  <div class=\"img\"><a href=\"https://www.jfinfo.com/news/20200228/2760425\"><img src=\"https://jfinfo.oss-cn-beijing.aliyuncs.com/file/upload/article/cover/3149123/5a8ca9e4-d530-4539-b261-e92c627ccf7c.png\" alt=\"5a8ca9e4 d530 4539 b261 e92c627ccf7c\" /><\/a><\/div>\n  <dl>\n    <dt><a class=\"f20\" target=\"_blank\" href=\"https://www.jfinfo.com/news/20200228/2760425\">金股预测晚间版：​南卫股份等3股后市备受关注<\/a>\n      <p class=\"cGray\">南卫股份（603880） 技术突破 ★★★投资要点：江苏南方卫材医药股份有限公司主要从事透皮产品、医用胶布胶带及绷带、运动保护产品、急救包、护理产品等产品的研发、生产和销售。目前已形成创可贴、贴...<\/p>\n    <\/dt>\n    <dd><i>金股晚间版<\/i><span>02-28 17:57<\/span><\/dd>\n  <\/dl>\n<\/div>');
            $("#bottom_load").data("value", true);
        }
        '''
        append_datas = eval(re.findall(r"append\((.*?)\);", more_page)[0])
        doc = html.fromstring(append_datas)
        news_list = doc.xpath(".//div[@class='slide']")
        items = []
        for news in news_list:
            item = {}
            title = news.xpath(".//a[@class='f20']/text()")[0].strip()
            # print(title)
            item['title'] = title
            link = news.xpath(".//a[@class='f20']/@href")[0]
            # print(link)
            item['link'] = link
            # 根据规律从 link 中获取当前的年份
            _year = None
            try:
                _year = re.findall(r"news/(\d+)/", link)[0][:4]   # 20161218
            except:
                pass
            pub_date = news.xpath(".//span/text()")[0].strip()
            pub_date = self._process_pub_dt(pub_date, _year)
            # print(">>> ", pub_date)
            item['pub_date'] = pub_date
            # print()
            detail_resp = self.get(link)
            if detail_resp:
                detail_page = detail_resp.text
                article = self._parse_detail(detail_page)
                item['article'] = article
                items.append(item)
                print(item)
        return items

    def _start(self):
        index_resp = self.get(self.index_url)
        if index_resp:
            index_page = index_resp.text
            index_items = self._parse_index(index_page)
            print(len(index_items))   # 20
            self.save(index_items)

        for num in range(1, self.max_page + 1):   # 目测目前有 639 页
            print(">>> ", num)
            more_url = self.more_url.format(num)
            print(more_url)
            more_resp = self.get(more_url)
            if more_resp:
                more_page = more_resp.text
                items = self._parse_more(more_page)
                print(len(items))   # 19
                print()
                self.save(items)


if __name__ == "__main__":
    r = Reference()
    r.start()
