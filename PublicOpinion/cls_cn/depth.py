import json
import random
import sys
import time
import requests
from gne import GeneralNewsExtractor

sys.path.append("./../../")
from PublicOpinion.cls_cn.cls_base import ClsBase
now = lambda: int(time.time())


class Depth(ClsBase):
    def __init__(self):
        super(Depth, self).__init__()
        self.this_last_dt = None
        self.name = '财联社-深度及题材'
        self.url_format = 'https://www.cls.cn/nodeapi/depths?last_time={}&refreshType=1&rn=20&sign=900569309a173964ce973dc61bbc2455'
        self.table = 'cls_depth_theme'
        self.extractor = GeneralNewsExtractor()

    def _parse_detail(self, url):
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            page = resp.text
            result = self.extractor.extract(page)
            content = result.get("content")
            return content

    def refresh(self, url):
        # 同样是递归地进行刷新以及调用
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            py_data = json.loads(resp.text)
            # print(py_data)
            # sys.exit(0)
            infos = py_data.get("data")
            # print(infos)
            if not infos:
                return
            items = []
            for info in infos:
                item = {}
                title = info.get("title")
                if not title:
                    title = info.get("content")[:20]
                item['title'] = title
                pub_date = info.get("ctime")

                article_id = info.get("article_id")
                item['link'] = "https://www.cls.cn/depth/{}".format(article_id)

                item['pub_date'] = self.convert_dt(pub_date)
                item['article'] = self._parse_detail(item['link'])
                items.append(item)
            self.save(items)
            # print(items)

            dt = infos[-1].get('ctime')
            if dt == self.this_last_dt:
                print("增量完毕 .. ")
                return
            self.this_last_dt = dt
            # dt - 1 是为了防止临界点重复值 尽量 insert_many 成功。
            next_url = self.url_format.format(dt-1)
            time.sleep(random.randint(1, 3))
            print("next_url: ", next_url)
            self.refresh(next_url)

    def _start(self):
        self._init_pool()
        first_url = self.url_format.format(now())
        self.refresh(first_url)

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
        ) ENGINE=InnoDB AUTO_INCREMENT=34657 DEFAULT CHARSET=utf8mb4 COMMENT='财联社-深度及题材' ; 
        '''
        ret = self.sql_pool._exec_sql(create_sql)
        self.sql_pool.end()
        return ret


if __name__ == "__main__":
    d = Depth()

    # d._init_pool()
    # ret = d._create_table()
    # print(ret)

    detail_url = 'https://www.cls.cn/depth/448106'
    ret = d._parse_detail(detail_url)
    print(ret)


    # d._start()