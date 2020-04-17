import datetime
import json
import random
import sys
import time
import traceback

import requests
requests.packages.urllib3.disable_warnings()
from gne import GeneralNewsExtractor

sys.path.append("./../../")
from PublicOpinion.cls_cn.cls_base import ClsBase
now = lambda: int(time.time())


class Depth(ClsBase):
    def __init__(self, format_url):
        super(Depth, self).__init__()
        self.this_last_dt = None
        self.name = '财联社-深度及题材'
        self.url_format = format_url
        self.table = 'cls_depth_theme'
        self.extractor = GeneralNewsExtractor()
        self.fields = ['title', 'link', 'pub_date', 'article']
        self.error_detail = []

    def _get(self, url):
        count = 0
        while True:
            try:
                count += 1
                if count > 3:
                    return
                resp = requests.get(url, headers=self.headers, verify=False, timeout=1)
            except requests.exceptions.ConnectionError:
                # print("connection error, retry ")
                time.sleep(1)
            except requests.exceptions.ReadTimeout:
                # print("read timeout, retry")
                time.sleep(1)
            except:
                return None
            else:
                break
        return resp

    def _parse_detail(self, url):
        resp = self._get(url)
        if resp and resp.status_code == 200:
            page = resp.text
            result = self.extractor.extract(page)
            content = result.get("content")
            return content
        else:
            self.error_detail.append(url)

    def refresh(self, url):
        # 数据一直到 2.19 在当前时间是 2.27 的情况下
        resp = self._get(url)
        if resp and resp.status_code == 200:
            py_data = json.loads(resp.text)
            infos = py_data.get("data")
            if not infos:
                return
            items = []
            for info in infos:
                item = {}
                title = info.get("title")
                if not title:
                    title = info.get("content")[:20]
                else:
                    if len(title) > 20:
                        title = title[:20]
                item['title'] = title
                article_id = info.get("article_id")
                item['link'] = "https://www.cls.cn/depth/{}".format(article_id)
                pub_date = info.get("ctime")
                item['pub_date'] = self.convert_dt(pub_date)
                article = self._parse_detail(item['link'])
                if article:
                    item['article'] = article
                    items.append(item)
            self.save(items)

            dt = infos[-1].get('ctime')
            if dt == self.this_last_dt:
                print("增量完毕")
                return
            self.this_last_dt = dt
            # dt - 1 是为了防止临界点重复值 尽量 insert_many 成功。
            next_url = self.url_format.format(dt-1)
            time.sleep(random.randint(1, 3))
            # print("next_url: ", next_url)
            self.refresh(next_url)

    def _start(self):
        self._init_pool()
        self._create_table()
        first_url = self.url_format.format(now())
        now_dt = lambda: datetime.datetime.now()
        print("{} {} {} 开始运行".format(now_dt(), self.name, self.url_format[: len("https://www.cls.cn/nodeapi/themes")]))
        for i in range(3):
            try:
                self.refresh(first_url)
            except:
                print("超时重试")
            else:
                print("成功")
                break
        print("请求失败的列表是: {}".format(self.error_detail))
        print("{} {} {} 运行结束".format(now_dt(), self.name, self.url_format[: len("https://www.cls.cn/nodeapi/themes")]))
        print()

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS `cls_depth_theme`(
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='财联社-深度及题材' ; 
        '''
        ret = self.sql_pool.insert(create_sql)
        self.sql_pool.end()
        return ret


class DepthSchedule(object):
    def start(self):
        depth_url_format = 'https://www.cls.cn/nodeapi/themes?lastTime={}&rn=20&sign=5055720fe645d52baf0ead85f70d220c'
        theme_url_format = 'https://www.cls.cn/nodeapi/depths?last_time={}&refreshType=1&rn=20&sign=900569309a173964ce973dc61bbc2455'
        Depth(depth_url_format)._start()
        Depth(theme_url_format)._start()


if __name__ == "__main__":
    sche = DepthSchedule()
    sche.start()
