import os
import re
import sys

import demjson
import requests

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from gne import GeneralNewsExtractor
from base import SpiderBase, logger


class NetEaseMoney(SpiderBase):
    table_name = "netease_money"
    dt_benchmark = 'pub_date'

    def __init__(self):
        super(NetEaseMoney, self).__init__()
        self.list_url = "http://money.163.com/special/00251G8F/news_json.js"
        self.extractor = GeneralNewsExtractor()
        self.fields = ['pub_date', 'title', 'link', 'article']

    def _parse_list(self, body):
        js_obj = re.findall(r"news:(.*)\};", body)[0]
        py_obj = demjson.decode(js_obj)
        for type in py_obj:  # 得到每一个子主题
            for data in type:
                yield data

    def _parse_detail(self, detail_url):
        try:
            page = requests.get(detail_url, headers=self.headers).text
            result = self.extractor.extract(page)
            content = result.get("content")
        except:
            return
        return content

    def get_list_resp(self):
        # TODO
        return requests.get(self.list_url, headers=self.headers)

    def _create_table(self):
        self._spider_init()
        sql = '''
        CREATE TABLE IF NOT EXISTS `{}` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`),
          KEY `update_time` (`UPDATETIMEJZ`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='网易财经'; 
        '''.format(self.table_name)
        self.spider_client.insert(sql)
        self.spider_client.end()

    def start(self):
        self._spider_init()
        self._create_table()

        list_resp = self.get_list_resp()
        logger.info("List Resp: {}".format(list_resp))
        if list_resp and list_resp.status_code == 200:
            body = list_resp.text
            ret = list(self._parse_list(body))
            items = []
            for one in ret:
                item = dict()
                link = one.get("l")
                item['link'] = link
                item['title'] = one.get("t")
                pub_date = one.get("p")
                item['pub_date'] = pub_date
                article = self._parse_detail(one.get("l"))

                if article:
                    item['article'] = article
                    items.append(item)
                    if len(items) > 30:
                        break
        else:
            raise Exception("请求无响应")

        if items:
            ret = self._batch_save(self.spider_client, items, self.table_name, self.fields)
            print(len(items))
            print(ret)


if __name__ == "__main__":
    NetEaseMoney().start()
