import json
import random
import time
import requests

# 方便测试
import sys
sys.path.append('./../../')
from PublicOpinion.cls_cn.cls_base import ClsBase

now = lambda: int(time.time())


class Telegraphs(ClsBase):
    def __init__(self):
        super(Telegraphs, self).__init__()
        self.this_last_dt = None
        self.name = '财新社-电报'
        self.url_format = 'https://www.cls.cn/nodeapi/telegraphs?refresh_type=1&rn=20&last_time={}&sign=56918b10789cb8a977c518409e7f0ced'
        self.table = 'cls_telegraphs'
        self.fields = ['title', 'pub_date', 'article']

    def refresh(self, url):
        # 只显示最近 24 小时的数据
        resp = requests.get(url, headers=self.headers, verify=False, timeout=1)
        # print(resp)
        if resp.status_code == 200:
            py_data = json.loads(resp.text)
            infos = py_data.get("data").get('roll_data')
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
                content = info.get("content")
                item['pub_date'] = self.convert_dt(pub_date)
                item['article'] = content
                items.append(item)
            self.save(items)

            dt = infos[-1].get('ctime')
            if dt == self.this_last_dt:
                print("增量完毕 .. ")
                return
            self.this_last_dt = dt
            # dt - 1 是为了防止临界点重复值 尽量 insert_many 成功
            next_url = self.url_format.format(dt-1)
            # 随机 sleep 模拟人的加载动作
            time.sleep(random.randint(1, 3))

            print("next_url: ", next_url)
            # TODO 递归的性能问题
            # 其实这个数据量应该还能承受, 递归的话逻辑会比较通顺
            # 后续看是否改为循环
            self.refresh(next_url)

    def _start(self):
        self._init_pool()
        first_url = self.url_format.format(now())
        self.refresh(first_url)

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS `cls_telegraphs`(
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `title` (`title`,`pub_date`),
          KEY `pub_date` (`pub_date`)
        ) ENGINE=InnoDB AUTO_INCREMENT=34657 DEFAULT CHARSET=utf8mb4 COMMENT='财联社-电报' ; 
        '''
        ret = self.sql_pool._exec_sql(create_sql)
        self.sql_pool.end()
        return ret


if __name__ == "__main__":
    # dt_test()
    # sys.exit(0)

    tele = Telegraphs()

    # tele._init_pool()
    # ret = tele._create_table()
    # print(ret)
    # sys.exit(0)

    tele._start()
