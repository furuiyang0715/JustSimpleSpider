import datetime
import json
import time

import requests

from base import SpiderBase

requests.packages.urllib3.disable_warnings()


class Telegraphs(SpiderBase):
    dt_benchmark = 'pub_date'
    table_name = 'cls_telegraphs'

    def __init__(self):
        super(Telegraphs, self).__init__()
        self.name = '财新社-电报'
        self.url_format = '''https://www.cls.cn/nodeapi/telegraphList?\
app=CailianpressWeb\
&category=\
&lastTime={}\
&last_time={}\
&os=web\
&refresh_type=1\
&rn=20\
&sv=7.2.2\
&sign=831bc324f5ad2f1119379cfc5b7ca0f0'''
        # self.url_format = 'https://www.cls.cn/nodeapi/telegraphs?refresh_type=1&rn=20&last_time={}&sign=56918b10789cb8a977c518409e7f0ced'
        self.fields = ['title', 'pub_date', 'article']
        self.desc = self.name

    def convert_dt(self, time_stamp):
        d = str(datetime.datetime.fromtimestamp(time_stamp))
        return d

    def refresh(self, url):
        resp = requests.get(url, headers=self.headers, verify=False, timeout=10)
        if resp.status_code == 200:
            py_data = json.loads(resp.text)
            infos = py_data.get("data").get('roll_data')
            if not infos:
                return
            items = []
            for info in infos:
                item = {}
                title = info.get("title")
                if not title:
                    title = info.get("content")[:20]
                item['title'] = title[:30]
                pub_date = info.get("ctime")
                content = info.get("content")
                item['pub_date'] = self.convert_dt(pub_date)
                item['article'] = content
                print(item)
                items.append(item)
            # 拿到本次最后一条新闻的时间
            dt = infos[-1].get('ctime')
            return items, dt

    def start(self):
        self._create_table()
        self._spider_init()
        _ts = int(time.time())
        first_url = self.url_format.format(_ts, _ts)
        items, last_dt = self.refresh(first_url)
        ret = self._batch_save(self.spider_client, items, self.table_name, self.fields)
        print(f"first 抓取数量{len(items)};入库数量{ret}")

        # 根据需要多久之前的数据,确定刷新的截止时间 cutoff_dt
        cutoff_dt = int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
        while last_dt > cutoff_dt:
            next_url = self.url_format.format(last_dt, last_dt)
            res = self.refresh(next_url)
            if res:
                items, last_dt = res
            else:
                return
            ret = self._batch_save(self.spider_client, items, self.table_name, self.fields)
            print(f"next 抓取数量{len(items)};入库数量{ret}")

    def _create_table(self):
        self._spider_init()
        create_sql = '''
        CREATE TABLE IF NOT EXISTS `{}`(
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `title` (`title`,`pub_date`),
          KEY `pub_date` (`pub_date`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='财联社-电报' ; 
        '''.format(self.table_name)
        self.spider_client.insert(create_sql)
        self.spider_client.end()


if __name__ == "__main__":
    tele = Telegraphs()
    tele.start()
