import json
import re
import traceback
from urllib.parse import urlencode

import pymongo
import requests
from bs4 import BeautifulSoup
from lxml import html
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ParseSpider(object):

    def make_query_params(self, code, timestamp):
        """
        拼接请求参数
        :param code:
        :param timestamp:
        :return:
        """
        query_params = {
            'stockCode': code,  # 查询股票代码
            'actionDate': timestamp,  # 只会按照数量返回这个时间戳之前的数据
            'perPageNum': self.perPageNum,  # 每次请求返回的个数
            "isOpen": "false",  # 不知道干嘛的一个参数 w(ﾟДﾟ)w
        }
        return query_params

    def _parse_page(self, url):
        """
        对文章详情页面进行解析
        """
        body = self.get(url).text
        # TODO 详情页的页数 1-n
        s_html = re.findall(r"<!-- 主贴内容开始 -->(.*?)<!-- 主贴内容结束 -->", body, re.S | re.M)[0]
        soup = BeautifulSoup(s_html, 'lxml')
        # 因为是要求文章中的图片被替换为链接放在相对应的位置所以这样子搞了w(ﾟДﾟ)w 之后看看有啥更好的办法
        imgs = soup.find_all(attrs={'data-type': 'contentImage'})
        if imgs:
            urls = [img['data-original'] for img in imgs]
            s_imgs = re.findall(r"<img.*?/>", s_html)  # 非贪婪匹配
            match_info = dict(zip(s_imgs, urls))
            for s_img in s_imgs:
                s_html = s_html.replace(s_img, match_info.get(s_img))
            # 替换之后再重新构建一次 这时候用 text 就直接拿到了 url ^_^
            soup = BeautifulSoup(s_html, 'lxml')
        text = soup.div.text.strip()
        return text

    def _parse_page_num(self, url):
        """
        判断当前的文章详情页文章一共分几页
        :param page:
        :return:
        """
        page = self.get(url).text
        doc = html.fromstring(page)
        page_num = doc.xpath("//div[@class='t_page right fy_pd3']/div[@class='left t_page01']")
        page_str = page_num[0].text_content()  # 末页下一页上一页首页共1/1页
        page_now, page_all = re.findall("共(.+)/(.+)页", page_str)[0]
        return page_now, page_all

    def parse_detail(self, item):
        durl = item['articleUrl']
        status_code = self.get(durl).status_code
        if status_code == 200:
            page_now, page_all = self._parse_page_num(durl)
            # logger.info(page_now, page_all)
            # 文章仅一页
            if page_all == "1" and page_now == page_all:
                logger.info("文章仅一页")
                content = self._parse_page(durl)
                logger.info(f"已经获取到当前页面的内容啦: --> {content[:10]}")
                return content

            # 一次爬取每一页再拼接起来
            else:
                content_dict = {}
                while int(page_now) <= int(page_all):
                    logger.info(f"开始爬取文章的第 {page_now} / {page_all} 页")
                    url = "https://www.taoguba.com.cn/Article/" + str(item["rID"]) + "/" + page_now
                    content_dict[page_now] = self._parse_page(url)
                    # logger.info(content_dict[page_now][:10])
                    page_now = str(int(page_now) + 1)
                return "\r\n".join(content_dict.values())
        elif status_code:
            raise Exception('详情页{}被反爬'.format(durl))

    def parse_list(self, code, name, url):
        response = self.get(url)
        if response.status_code == 200:
            records = json.loads(response.text).get("dto", {}).get("record")
            if records:
                for record in records:
                    #  如果是原文的话这里是 None
                    #  转评的话 这里是有内容的 爬取规则是只要原文 不要转评
                    #  同时 原文的 rtype' 是 'T', 转评的  'rtype'是 'R'
                    if record.get("tops") and record.get("rtype") == "R":
                        # logger.info("此内容为转评, 略去")
                        continue

                    article_url = "https://www.taoguba.com.cn/Article/" + str(record.get("rID")) + "/1"
                    item = {}
                    item['stockCode'] = code
                    item['ChiNameAbbr'] = name
                    item["actionDate"] = record.get("actionDate")   # 文章发布时间
                    item['body'] = record.get("body")  # 文章摘要
                    item['subject'] = record.get("subject")  # 文章标题
                    item['userName'] = record.get("userName")  # 用户名 即消息来源
                    item['gnName'] = record.get("gnName")   # 文章谈及概念   TODO list 和 dict 在入库之前再处理
                    item['stockAttr'] = record.get("stockAttr")   # 文章谈及股票
                    # article_url = "https://www.taoguba.com.cn/Article/" + str(record.get("rID")) + "/1"
                    item['articleUrl'] = article_url
                    # 增加一个方便翻页的参数
                    item['rID'] = record.get("rID")
                    logger.info(item)
                    self.insert_list_info(item)

                # 生成下一次爬取的 url 相当于翻页
                more_timestamp = records[-1].get("actionDate")
                more_url = self.list_url + urlencode(self.make_query_params(code, more_timestamp))
                self.parse_list(code, name, more_url)
            else:   # 说明该数据已经爬取完毕了
                logger.info('结束的url是{}'.format(url))
                logger.info("股票{}的列表页已经全部入库了".format(name))
        else:
            # 请求结果的状态码不是 200 记录一下
            logger.warning("{} 请求异常， 异常 url 是{}".format(code, url))
            self.error_list.append(url)