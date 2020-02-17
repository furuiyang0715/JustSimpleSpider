import datetime
import json
import random
import re
import string
import time
from urllib.parse import urlencode

import requests as req
from lxml import html

from cnstock.hongguan import CNStock


class CNStock_2(CNStock):
    # 适用于 上证四小时
    def __init__(self, *args, **kwargs):
        super(CNStock_2, self).__init__(*args, **kwargs)
        self.list_url = "http://app.cnstock.com/api/theme/get_theme_list?"

    def make_query_params(self, latest_id):
        """
        拼接动态请求参数
        """
        query_params = {
            'maxid': str(0),
            'minid': str(latest_id),   # 这个越大的是越新的内容
            'size': 5,
            'callback': 'jQuery{}_{}'.format(
                ''.join(random.choice(string.digits) for i in range(0, 20)),
                str(int(time.time() * 1000))
            ),
            '_': str(int(time.time() * 1000)),
        }
        return query_params

    def get_zhaiyao(self, url):
        try:
            page = req.get(url, headers=self.headers).text
            doc = html.fromstring(page)
            detail_link = doc.xpath("//div[@class='tcbhd-r']//h1/a/@href")[0]
            return detail_link
        except:
            return None

    def get_count(self):
        params = self.make_query_params(0)
        url = self.list_url + urlencode(params)
        ret = req.get(url, headers=self.headers).text
        json_data = re.findall(r'jQuery\d{20}_\d{13}\((\{.*?\})\)', ret)[0]
        py_data = json.loads(json_data)
        count = py_data.get("item")[0].get("order")
        return count + 1

    def get_list(self):
        count = self.get_count()
        print(count)
        for latest_id in range(count, 0, -5):
            print(latest_id)
            params = self.make_query_params(latest_id)
            url = self.list_url + urlencode(params)
            ret = req.get(url, headers=self.headers).text
            json_data = re.findall(r'jQuery\d{20}_\d{13}\((\{.*?\})\)', ret)[0]
            py_data = json.loads(json_data)
            # print(py_data)
            datas = py_data.get("item")
            if not datas:
                break
            for one in datas:
                item = dict()

                pub_date = datetime.datetime.strptime(one.get("datetime"), "%Y-%m-%d %H:%M:%S")
                if pub_date < self.check_date:
                    print("增量完毕\n")
                    return

                item['pub_date'] = one.get("datetime")
                item['title'] = one.get("title")
                item['zhaiyao'] = 'http://news.cnstock.com/theme,{}.html'.format(one.get("id"))
                yield item

    def start(self):
        count = 0
        for item in self.get_list():
            if item:
                zhaiyao_link = item.get('zhaiyao')
                detail_url = self.get_zhaiyao(zhaiyao_link)
                if detail_url:
                    item['link'] = detail_url
                    item['article'] = self.get_detail(detail_url)
                    item.pop("zhaiyao")
                    print(item)
                    ret = self._save(item)
                    count += 1
                    if ret:
                        print("插入成功 ")
                        pass
                    else:
                        # print("插入失败 ")
                        self.error_detail.append(item.get("link"))
                    if count > 10:
                        self.sql_pool.connection.commit()
                        count = 0


if __name__ == "__main__":
    runner = CNStock_2()   # 上证4小时
    runner.start()
    print(runner.error_detail)
