import json
import re
import sys
import time

import demjson
import requests

from money_163.threading_pool import BaseSpider


class Money163(BaseSpider):
    def __init__(self):
        super(Money163, self).__init__()
        self.list_url = "http://money.163.com/special/00251G8F/news_json.js"
        # 初始化容量为 16 的线程池
        self.init_thread(16)

    def _parse_list(self, body):
        # 将每一页的 item 存进队列 之后这一步也是并发执行
        js_obj = re.findall(r"news:(.*)\};", body)[0]
        # py_obj = json.loads(js_obj)
        # print(py_obj)

        py_obj = demjson.decode(js_obj)
        # print(py_obj)

        for type in py_obj:  # 得到每一个子主题
            # print(type)  # list of dict
            for data in type:
                # print(data)
                self.put(data)

    def _start(self):
        now = lambda: time.time()
        start_time = now()

        list_resp = requests.get(self.list_url)
        if list_resp.status_code == 200:
            body = list_resp.text
            self._parse_list(body)

        # 从队列中获取item
        while True:
            item = self.get()
            if not item:
                break

            # print("拿到了{}".format(item))
            # 获取到一个可用的空闲线程
            a_thread = self.get_available()
            # 将数据赋值给该线程
            a_thread.datas = item
            # 将当前线程添加到当前爬虫实例的活跃线程中去
            if a_thread:
                self.running_thread.append(a_thread)
                a_thread.start()

        # 等待全部的线程运行完毕
        for t in self.running_thread:
            if t.isAlive():
                t.join()

        # 结束时间
        end_time = time.time()
        print(len(self.running_thread), '个线程, ', '运行时间: ', end_time - start_time, '秒')
        print('空余线程数: ', len(self.threads_pool))


if __name__ == "__main__":
    m = Money163()
    m._start()
