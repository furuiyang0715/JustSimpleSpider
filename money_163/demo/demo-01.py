#-*- coding:utf-8 -*-

import json
import pprint
import re
import sys

import demjson

import requests as req
from gne import GeneralNewsExtractor
from selenium.webdriver import Chrome


def test1():
    url = "http://money.163.com/latest/"
    ret = req.get(url)
    body = ret.text
    print(body)
    print("大数据" in body)


def test2():
    url = "http://money.163.com/latest/"
    driver = Chrome()
    driver.get(url)
    page = driver.page_source
    # print(page)
    print("大数据看600家" in page)


def test3():
    url = "http://money.163.com/special/00251G8F/news_json.js?0.37005690223201015"
    ret = req.get(url).text
    # print(ret)
    ret = re.findall(r"news:\[\[(.*)\]\]\};", ret)[0]
    print(ret)
    news = ret.split("},")
    print(news)


def test4():
    url = "http://money.163.com/special/00251G8F/news_json.js?0.37005690223201015"
    ret = req.get(url).text
    ret = re.findall(r"news:\[(.*)\]\};", ret)[0]
    c = "c"
    t = "t"
    l = "l"
    p = "p"
    # print(ret)
    print(type(ret))
    # ret = ret[0]
    ret = json.loads(ret)


def test5():
    # https://cloud.tencent.com/developer/ask/175357
    url = "http://money.163.com/special/00251G8F/news_json.js?0.37005690223201015"
    ret = req.get(url).text
    js_obj = re.findall(r"news:\[(.*)\]\};", ret)[0]
    print(js_obj)
    # py_obj = demjson.decode(js_obj)
    # print(py_obj)


def test6():
    import json, _jsonnet

    # # from
    # js_obj = '{x:1, y:2, z:3}'
    #
    # # to
    # py_obj = json.loads(_jsonnet.evaluate_snippet('snippet', js_obj))
    # print(py_obj)

    url = "http://money.163.com/special/00251G8F/news_json.js?0.37005690223201015"
    ret = req.get(url).text
    js_obj = re.findall(r"news:\[(.*)\]\};", ret)[0]
    # print(js_obj[31499])
    py_obj = json.loads(_jsonnet.evaluate_snippet('snippet', js_obj))
    print(py_obj)


def test7():
    url = "http://money.163.com/special/00251G8F/news_json.js?0.37005690223201015"
    ret = req.get(url).text
    js_obj = re.findall(r"news:(.*)\};", ret)[0]
    """
    [
     [{}, {}, {}, {}],
     [{}, {}, {}, {}], 
     [{}, {}, {}, {}]
     ]
    """
    # print(js_obj)
    # print(js_obj[:100])
    # print(js_obj[-100:])
    # sys.exit(0)
    py_obj = demjson.decode(js_obj)
    # print(py_obj)
    for type in py_obj:  # 得到每一个子主题
        print(type)
        print()

    sys.exit(0)
    js_obj = js_obj
    news = js_obj.split("")
    # errors = []
    for new in news:
        print(new)
        # py_new = None
        # try:
        #     if new.endswith("}]"):
        #         new = new.rstrip("]")
        #         py_new = demjson.decode(new)
        #     elif not new.endswith("}"):
        #         py_new = demjson.decode(new + '}')
        #     else:
        #         py_new = demjson.decode(new)
        # except:
        #     errors.append(new)
        #
        # # print(py_new)

    # for e in errors:
    #     print(e)


def test8():
    extractor = GeneralNewsExtractor()
    detail = "https://money.163.com/20/0212/14/F56LIPN500259DLP.html"
    page = req.get(detail).text
    print("今天来聊个话题，如果拉长" in page)
    result = extractor.extract(page)
    ret = result.get("content")
    print(ret)








test8()
