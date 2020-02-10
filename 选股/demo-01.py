# -*- coding: utf-8 -*-
# @Time    : 2020/1/5 下午9:41
# @File    : 问财选股.py
from copyheaders import headers_raw_to_dict
import requests
import json
import csv
import time
import re


def save_item_in_csv(file_name, item, titleNum=0):
    """保存数据item到csv里面，方式a"""
    with open(file_name, "a", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=item.keys())
        if titleNum == 0:
            writer.writeheader()
        writer.writerow(item)


def get_stock_list():
    url = 'http://www.iwencai.com/unifiedwap/unified-wap/result/get-stock-pick'
    # data = 'question=A股清单&secondary_intent=stock&perpage=100&page=2&sort_key=股票市场类型&sort_order=DESC&query_area=&block_list=&token=290ed60880035347ed4a4ff58706669a&add_info={"urp":{"scene":1,"company":1,"business":1}}&fund_class=&show_indexes=["最新价","最新涨跌幅","股票市场类型"]'
    # data = {i.split("=")[0]: i.split("=")[1] for i in data.split("&")}
    data = {'question': 'A股清单', 'secondary_intent': 'stock', 'perpage': '100', 'page': '1', 'sort_key': '股票市场类型',
            'sort_order': 'DESC', 'query_area': '', 'block_list': '', 'token': '290ed60880035347ed4a4ff58706669a',
            'add_info': '{"urp":{"scene":1,"company":1,"business":1}}', 'fund_class': '',
            'show_indexes': '["最新价","最新涨跌幅","股票市场类型"]'}
    headers = b'''
    Accept: */*
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: keep-alive
    Content-Length: 494
    Content-Type: application/x-www-form-urlencoded
    Cookie: chat_bot_session_id=83ee8dd06344926d66b4e8ab86154ebf; cid=4faba29b39709c026aa6c2338ee9cc2c1578054633; ComputerID=4faba29b39709c026aa6c2338ee9cc2c1578054633; user=MDpjYmoxOTQ2NTk5MzE6Ok5vbmU6NTAwOjIyMzc5OTU5Njo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxLDQwOzIsMSw0MDszLDEsNDA7NSwxLDQwOzgsMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDEsNDA6Mjc6OjoyMTM3OTk1OTY6MTU3Nzg3MDU0NDo6OjE0MjE2NTUxMjA6NDAxODU2OjA6MTJkYTNhOWM5NDZlMDk4MTlmYWI4MTQzYzVhMzJhOTU5OmRlZmF1bHRfNDow; userid=213799596; u_name=cbj194659931; escapename=cbj194659931; ticket=2dc4eeac754f23d22f86ad12c08f5f1b; ver_mark=d; PHPSESSID=4d2f5e4a06d4fc7104c9058ea9a0afba; guideState=1; v=AsEVbjyXewEpB5c1dXHhLjPg1gbY7jXoX2LZ9CMWvUgnCu9waz5FsO-y6cKw; other_uid=Ths_iwencai_Xuangu_07448614b981497686ae179fa640e9a8
    Host: www.iwencai.com
    Origin: http://www.iwencai.com
    Referer: http://www.iwencai.com/unifiedwap/result?w=A%E8%82%A1%E6%B8%85%E5%8D%95&querytype=&issugs
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36
    '''
    response = requests.post(url, headers=headers_raw_to_dict(headers), data=data)
    response = json.loads(response.text)
    total_count = response.get("data").get("analyze_data").get("total")
    for i in response.get("data").get("data"):
        item = dict()
        item["total_count"] = total_count
        item["marketId"] = i.get("marketId")
        item["code"] = i.get("hqCode")
        item["name"] = i.get("股票简称")
        item["price"] = i.get("最新价")
        print(item)
        save_item_in_csv("1.stock_list.csv", item)

    total_page = total_count // 100 + 1
    for page in range(2, total_page + 1):
        data = {'question': 'A股清单', 'secondary_intent': 'stock', 'perpage': '100', 'page': str(page),
                'sort_key': '股票市场类型',
                'sort_order': 'DESC', 'query_area': '', 'block_list': '', 'token': '290ed60880035347ed4a4ff58706669a',
                'add_info': '{"urp":{"scene":1,"company":1,"business":1}}', 'fund_class': '',
                'show_indexes': '["最新价","最新涨跌幅","股票市场类型"]'}
        response = requests.post(url, headers=headers_raw_to_dict(headers), data=data)
        response = json.loads(response.text)
        total_count = response.get("data").get("analyze_data").get("total")
        for i in response.get("data").get("data"):
            item = dict()
            item["total_count"] = total_count
            item["marketId"] = i.get("marketId")
            item["code"] = i.get("hqCode")
            item["name"] = i.get("股票简称")
            item["price"] = i.get("最新价")
            print(item)
            save_item_in_csv("1.stock_list.csv", item)


# 传入question的词，获取得到的股票。注意：如果搜索的是产品就没有概念描述之类的，如果搜索的是概念就没有产品的描述之类的。
def get_stock_concept():
    "http://www.iwencai.com/unifiedwap/result?w=%E5%8D%B0%E5%88%B6%E7%94%B5%E8%B7%AF%E6%9D%BF%EF%BC%8C%E6%9F%94%E6%80%A7%E7%94%B5%E8%B7%AF&querytype=&issugs"
    url = 'http://iwencai.com/unifiedwap/unified-wap/result/get-stock-pick'
    data = {'question': '印制电路板', 'secondary_intent': 'stock', 'condition_id': '', 'perpage': '50'}
    response = requests.post(url, data=data)
    response = json.loads(response.text)
    print("一共获取到了{}条记录。".format(len(response.get("data").get("data"))))
    for i in response.get("data").get("data"):
        item = dict()
        item["code"] = i.get("股票代码")
        item["short_code"] = i.get("hqCode")
        item["marketId"] = i.get("marketId")
        item["name"] = i.get("股票简称")
        item["price"] = i.get("最新价")
        item["capital"] = i.get("总股本[{}]".format(str_now_day))
        item["pe"] = i.get("市盈率(pe)[{}]".format(str_now_day))
        item["value"] = i.get("a股市值(不含限售股)[{}]".format(str_now_day))
        item["ths_industry"] = i.get("所属同花顺行业")
        item["product"] = i.get("主营产品名称")
        item["concept"] = i.get("所属概念")
        item["concept_intro"] = i.get("概念解析")
        item["concept_nums"] = i.get("所属概念数量")
        item["business_scope"] = i.get("经营范围")
        item["company_url"] = i.get("公司网站")
        print(item)


# 传入股票名称获取所属同花顺二级行业板块、城市、产品、概念（这个很重要！！！）
def stock_product_and_concept():
    url = 'http://iwencai.com/unifiedwap/unified-wap/result/get-robot-data?source=Ths_iwencai_Xuangu&version=2.0&secondary_intent='
    data = {
        'question': '航发科技',
        'add_info': '{"urp":{"scene":1,"company":1,"business":1}}'
    }

    response = requests.post(url, data=data)
    response = json.loads(response.text)
    content = response.get("data").get("answer")[0].get("txt")[0].get("content")
    content = json.loads(content)
    for i in content.get("components")[0].get("data"):
        item = dict()
        item["name"] = i.get("股票简称")
        item["code"] = i.get("股票代码")
        item["short_code"] = re.findall(r'(.*?)\.', item["code"])[0]
        item["city"] = i.get("城市")
        item["ths_industry"] = i.get("所属同花顺二级行业")
        item["product"] = i.get("主营产品名称").replace("||", ",")
        item["concept"] = i.get("所属概念").replace(";", ",")
        print(item)


if __name__ == '__main__':
    get_stock_list()
    # str_now_day = time.strftime("%Y-%m-%d", time.localtime(time.time())).replace('-', '')
    # stock_product_and_concept()
