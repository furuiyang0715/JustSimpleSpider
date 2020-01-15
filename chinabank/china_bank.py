# -*- coding: utf-8 -*-

import datetime
import math
import pprint
import re
import time
import traceback

from lxml import html
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from chinabank.my_log import logger
from chinabank.sys_info import Recorder
from chinabank.configs import MYSQL_TABLE, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from chinabank.common.sqltools.mysql_pool import MyPymysqlPool, MqlPipeline


class ChinaBank(object):
    """
    中国银行爬虫
        爬取两个模块：
        （1） 数据解读
        （2） 新闻发布
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
        if MYSQL_TABLE == "chinabank_shujujiedu":
            self.url = 'http://www.pbc.gov.cn/diaochatongjisi/116219/116225/11871/index{}.html'

        elif MYSQL_TABLE == "chinabank_xinwenfabu":
            self.url = 'http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/11040/index{}.html'

        else:
            raise RuntimeError("请检查数据起始 url")

        # self.browser = webdriver.Chrome()    # local

        # TODO 可能还没有启动 就会出现 refused 的问题
        # TODO 暂时是使用了一个比较 ugly 的方法 强制在这里暂停 30 s
        # TODO 应该有办法去 ping 一下服务端 返回一个服务是否已经就绪的状态
        time.sleep(30)
        self.browser = webdriver.Remote(
            # command_executor="http://{}:4444/wd/hub".format(SELENIUM_HOST),    # docker
            command_executor="http://chrome:4444/wd/hub",   # compose
            desired_capabilities=DesiredCapabilities.CHROME
        )

        self.browser.implicitly_wait(30)  # 隐性等待，最长等30秒

        self.sql_client = MyPymysqlPool(
            {
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "user": MYSQL_USER,
                "password": MYSQL_PASSWORD,
            }
        )

        self.db = MYSQL_DB
        self.table = MYSQL_TABLE
        self.pool = MqlPipeline(self.sql_client, self.db, self.table)

        self.record = Recorder(False)   # sqlite 数据库记录爬取情况

        self.error_list = []

    def save_to_mysql(self, item):
        self.pool.save_to_database(item)

    def crawl_list(self, offset):
        list_page = self.get_page(self.url.format(offset))
        item_list = self.parse_list_page(list_page)
        return item_list

    def get_page(self, url):
        self.browser.get(url)
        return self.browser.page_source

    def parse_table(self, zoom):
        my_table = zoom.xpath("./table")[0]
        trs = my_table.xpath("./tbody/tr")
        table = []
        for tr in trs:
            tr_line = []
            tds = tr.xpath("./td")
            for td in tds:
                tr_line.append(td.text_content())
            table.append(tr_line)
        return "\r\n" + "{}".format(table)

    def parse_detail_page(self, detail_page):
        doc = html.fromstring(detail_page)
        zoom = doc.xpath("//div[@id='zoom']")[0]
        try:
            table = self.parse_table(zoom)
        except:
            table = []
        if table:
            contents = []
            for node in zoom:
                if node.tag == "table":
                    pass
                    # 表格不需要 也不需要替换 pdf
                    # contents.append(self.parse_table(zoom))
                else:
                    contents.append(node.text_content())
            return "".join(contents)

        else:
            detail_content = zoom.text_content()
            return detail_content

    def parse_list_page(self, list_page):
        doc = html.fromstring(list_page)
        news_area = doc.xpath("//div[@opentype='page']")[0]
        news_title_parts = news_area.xpath("//font[@class='newslist_style']")
        items = []

        for news_title_part in news_title_parts:
            item = {}
            # TODO 应对 105, 109, 112 等不太符合规范的列表页
            try:
                news_date_part = news_title_part.xpath("./following-sibling::span[@class='hui12']")[0].text_content()
            except:
                news_date_part = news_title_part.xpath("./following-sibling::a/span[@class='hui12']")[0].text_content()
            # print(news_date_part)
            item["pubdate"] = news_date_part   # 发布时间

            news_title = news_title_part.xpath("./a")[0].text_content()
            # print(news_title)
            item["article_title"] = news_title  # 文章标题

            news_link = news_title_part.xpath("./a/@href")[0]
            news_link = "http://www.pbc.gov.cn" + news_link
            item["article_link"] = news_link  # 文章详情页链接
            # print(news_link)
            items.append(item)

        return items

    def yyyymmdd_date(self, dt: datetime.datetime) -> int:
        """
        将 datetime 转换为 date_int 格式
        datetime.datetime(2020,1,1) --> 20200101
        :param dt:
        :return:
        """
        return dt.year * 10 ** 4 + dt.month * 10 ** 2 + dt.day

    def parse_info(self):
        """
        <td nowrap="true" align="left" valign="bottom" style="width:40%;" class="Normal">
            总记录数:3897,每页显示15条记录,当前页:
            <font color="red" style="font-family:雅黑,宋体">1</font>
            /260
        </td>
        """
        f_url = self.url.format(1)
        page = None

        for i in range(3):
            try:
                self.browser.get(f_url)
                page = self.browser.page_source
            except:
                pass
            else:
                break
        if not page:
            raise RuntimeError

        doc = html.fromstring(page)
        cur_page = doc.xpath("//font[@color='red']")[0]
        # print(cur_page)  # <Element font at 0x1106d7230>
        all_page_info = cur_page.xpath("./..")[0]
        # print(all_page_info)  # <Element td at 0x10dff41d0>
        cur = cur_page.text_content()
        # print(cur)   # 1

        all_page = all_page_info.text_content()
        # print(all_page)  # 总记录数:3897,每页显示15条记录,当前页: 1 /260
        (nums, pages) = re.findall("总记录数:(\d+),每页显示(\d+)条记录", all_page)[0]
        nums = int(nums)
        per_page_num = int(pages)
        dt_int = self.yyyymmdd_date(datetime.datetime.today())

        return dt_int, nums, per_page_num

    def close(self):
        logger.info("爬虫关闭 ")
        self.browser.close()
        self.sql_client.dispose()

    def start(self):
        # 从数据库中取出上一次的更新情况
        last_info = self.record.get_last()
        this_info = self.parse_info()

        logger.info("上次的记录是{}".format(last_info))
        logger.info("本次爬取的记录是{}".format(this_info))

        if (last_info[0] == this_info[0]) or (last_info[1] == this_info[1]):
            if last_info[0] == this_info[0]:
                logger.info("时间是同一天 {}, 不再爬取".format(last_info[0]))
            elif last_info[1] == this_info[1]:
                logger.info("文章个数无新增 {}, 不再爬取".format(last_info[1]))
                # 同一天的时候插入会造成主键冲突
                self.record.insert(*this_info)

            logger.info("刷新记录{}".format(this_info))
            self.close()
            return

        else:
            self.pages = math.ceil((this_info[1] - last_info[1]) / this_info[2])
            logger.info("ceil[({} - {}) / {}]".format(this_info[1], last_info[1], this_info[2]))
            logger.info("计算得到需要爬取的页数是 {}".format(self.pages))

        for page in range(1, self.pages + 1):
            retry = 3
            while True:
                try:
                    # 总的来说 是先爬取到列表页 再根据列表页里面的链接去爬取详情页
                    items = self.crawl_list(page)

                    for item in items:
                        detail_page = self.get_page(item["article_link"])
                        item['article_content'] = self.parse_detail_page(detail_page)
                        self.save_to_mysql(item)
                except Exception as e:
                    logger.warning("加载出错了,重试, the page is {}".format(page))
                    time.sleep(3)    # 休息 3 s 再次请求
                    traceback.print_exc()
                    retry -= 1
                    if retry < 0:
                        self.error_list.append(page)
                        break
                else:
                    logger.info("本页保存成功 {}".format(page))
                    break

        self.record.insert(*this_info)

        self.close()
