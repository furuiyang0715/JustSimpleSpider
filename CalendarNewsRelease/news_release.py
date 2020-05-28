# coding=utf8
import json
import os
import csv
import datetime
import requests as req
from lxml import html

from base import SpiderBase


class SaveCSV(object):

    def save(self, keyword_list, path, item):
        """
        保存csv方法
        :param keyword_list: 保存文件的字段或者说是表头
        :param path: 保存文件路径和名字
        :param item: 要保存的字典对象
        :return:
        """
        try:
            # 第一次打开文件时，第一行写入表头
            if not os.path.exists(path):
                with open(path, "w", newline='', encoding='utf-8') as csvfile:  # newline='' 去除空白行
                    writer = csv.DictWriter(csvfile, fieldnames=keyword_list)  # 写字典的方法
                    writer.writeheader()  # 写表头的方法

            # 接下来追加写入内容
            with open(path, "a", newline='', encoding='utf-8') as csvfile:  # newline='' 一定要写，否则写入数据有空白行
                writer = csv.DictWriter(csvfile, fieldnames=keyword_list)
                writer.writerow(item)  # 按行写入数据
                print("{} Write success".format(item))

        except Exception as e:
            print("Write error:", e)
            # 记录错误数据
            with open("error.txt", "w") as f:
                f.write(json.dumps(item) + ",\n")


class CalendarNews(SpiderBase):
    month_map = {
        "一月": 1,
        "二月": 2,
        "三月": 3,
        "四月": 4,
        "五月": 5,
        "六月": 6,
        "七月": 7,
        "八月": 8,
        "九月": 9,
        "十月": 10,
        "十一月": 11,
        "十二月": 12,
    }

    key_words = [
        '国庆节',
        '八号台风信号(天鸽)',
        '圣诞节',
        '元旦',
        '春节',
        '耶稣受难节',
        '复活节',
        '清明节',
        '劳动节',
    ]

    def __init__(self, save_type='csv'):
        super(CalendarNews, self).__init__()
        self.url = 'https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/News/News-Release?sc_lang=zh-HK&Year=ALL&NewsCategory=&currentCount={}'.format(2000)
        self.table_name = 'calendar_news'
        self.fields = ['PubDate', 'NewsTag', 'NewsUrl', 'NewsTitle']
        self.save_type = save_type
        self.client = None

    def __del__(self):
        if self.client:
            self.client.dispose()

    def _create_table(self):
        self.client = self._init_pool(self.spider_cfg)
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'ID',
          `PubDate` datetime NOT NULL COMMENT '新闻发布时间',
          `NewsTag` varchar(20) NOT NULL COMMENT '新闻类别标签', 
          `NewsUrl` varchar(200) DEFAULT NULL COMMENT '链接', 
          `NewsTitle` varchar(200) DEFAULT NULL COMMENT '标题',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `un2` (`PubDate`, `NewsUrl`) USING BTREE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='交易所日历新闻';
        '''.format(self.table_name)
        self.client.insert(sql)
        self.client.end()

    def get_items(self):
        resp = req.get(self.url)
        if resp.status_code == 200:
            page = req.get(self.url).text
            doc = html.fromstring(page)
            news = doc.xpath("//div[@class='news-releases']/div[@class='news-releases__section']")
            items = []
            for one in news:
                item = dict()
                _date = one.xpath("./div[@class='news-releases__section--date']/div[@class='news-releases__section--date-day']")[0].text_content()
                _month = one.xpath("./div[@class='news-releases__section--date']/div[@class='news-releases__section--date-month']")[0].text_content()
                _year = one.xpath("./div[@class='news-releases__section--date']/div[@class='news-releases__section--date-year']")[0].text_content()

                _month = self.month_map.get(_month)
                _date = int(_date)
                _year = int(_year)
                news_dt = datetime.datetime(_year, _month, _date)
                try:
                    news_tag = one.xpath(".//span[@class='tag-yellow  tag-yellow-triangle tag-first']")[0].text_content()
                except:
                    news_tag = None
                try:
                    news_url = one.xpath(".//a[@class='news-releases__section--content-title']/@href")[0]
                    news_title = one.xpath(".//a[@class='news-releases__section--content-title']")[0].text_content()
                except:
                    news_url = one.xpath(".//a[@class='news-releases__section--content-title ']/@href")[0]
                    news_title = one.xpath(".//a[@class='news-releases__section--content-title ']")[0].text_content()

                if news_dt and news_tag and news_url and news_title:
                    item['PubDate'] = news_dt
                    item['NewsTag'] = news_tag
                    item['NewsUrl'] = news_url
                    item['NewsTitle'] = news_title.strip()
                    items.append(item)

            return items
        else:
            print(resp.status_code)
            return None

    def save_csv(self, items):
        s = SaveCSV()
        file_path = 'taifeng.csv'
        all_file_path = 'news_release.csv'
        for item in items:
            news_title = item.get("NewsTitle")
            if "台风" in news_title:
                s.save(self.fields, file_path, item)
            s.save(self.fields, all_file_path, item)

    def start(self):
        items = self.get_items()
        if not items:
            return

        if self.save_type == "csv":
            self.save_csv(items)
        elif self.save_type == "sql":
            self._create_table()
            print(len(items))
            self._batch_save(self.client, items, self.table_name, self.fields)
        else:
            print("未知的存储方式")


if __name__ == "__main__":
    # CalendarNews(save_type="csv").start()

    CalendarNews(save_type="sql").start()
