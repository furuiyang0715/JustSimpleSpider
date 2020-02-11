import json
import re
import sys

import demjson
import requests

from money_163.threading_pool import BaseSpider


class Money163(BaseSpider):
    def __init__(self):
        super(Money163, self).__init__()
        self.list_url = "http://money.163.com/special/00251G8F/news_json.js?0.37005690223201015"

        pass

    def _parse_list(self, body):
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
        list_resp = requests.get(self.list_url)
        if list_resp.status_code == 200:
            body = list_resp.text
            self._parse_list(body)


        pass


if __name__ == "__main__":
    m = Money163()
    m._start()

