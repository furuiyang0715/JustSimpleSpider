# -*- coding: utf-8 -*-
import base64
import os
import re
import sys
import requests
from retrying import retry
from gne import GeneralNewsExtractor
from lxml import html
cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base import SpiderBase
from configs import LOCAL


class GovBaseSpider(SpiderBase):
    def __init__(self):
        super(GovBaseSpider, self).__init__()
        self.extractor = GeneralNewsExtractor()
        self.local = LOCAL

    def fetch_page(self, url):
        try:
            page = self.js_get_page(url)
        except:
            return None
        else:
            return page

    def _get_refer_url(self, body):
        """获取重定向之后的网址"""
        doc = html.fromstring(body)
        script_content = doc.xpath("//script")[0].text_content()
        re_str = r"var(.+?).split"
        ret = re.findall(re_str, script_content)[0]
        # print("正则结果: ", ret)
        ret = ret.lstrip("|(")
        ret = ret.rstrip("')")
        ret_lst = ret.split("|")
        names = ret_lst[0::2]
        params = ret_lst[1::2]
        info = dict(zip(names, params))
        factor = sum([ord(ch) for ch in info.get("wzwsquestion")]) * int(info.get("wzwsfactor")) + 0x1b207
        raw = f'WZWS_CONFIRM_PREFIX_LABEL{factor}'
        refer_url = info.get("dynamicurl") + '?wzwschallenge=' + base64.b64encode(raw.encode()).decode()
        return "http://www.pbc.gov.cn" + refer_url

    @retry(stop_max_attempt_number=10)
    def js_get_page(self, url):
        s = requests.Session()
        h1 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'www.pbc.gov.cn',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
        }
        resp1 = s.get(url, headers=h1)
        cookie1 = resp1.headers.get("Set-Cookie").split(";")[0]
        origin_text = resp1.text
        redirect_url = self._get_refer_url(origin_text)
        h1.update({
            'Cookie': cookie1,
            'Referer': 'http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/11040/index1.html',
        })
        resp2 = s.get(redirect_url, headers=h1)
        text = resp2.text.encode("ISO-8859-1").decode("utf-8")
        # import time
        # time.sleep(1)
        return text

    def gne_parse_detail(self, page):
        result = self.extractor.extract(page)
        content = result.get("content")
        return content
