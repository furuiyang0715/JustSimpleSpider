# 实现请求去重的逻辑
import sys
import urllib.parse

from filter_tools import get_filter_class
from request_tools.my_requests import Request


class RequestFilter(object):
    def __init__(self, filter_obj):
        self.filter_obj = filter_obj

    def get_request_filter_data(self, request_obj):
        """
        从请求对象中组合出判断去重的数据
        :param request_obj:
        :return:
        """
        # 将协议和域名部分进行大小写统一 其余的保留原始的大小写格式
        # 处理 url 的几个模块：
        # import urllib.parse
        # import w3lib.url

        # 方法名统一大写
        method = request_obj.method.upper()

        url = request_obj.url
        _ = urllib.parse.urlparse(url)
        url_without_query = _.scheme + "://" + _.hostname + _.path

        url_query = urllib.parse.parse_qsl(_.query)
        if not url_query:
            url_query = []
        query = request_obj.query
        if not query:
            query = {}

        query = list(query.items())
        # 将 url 里面的请求参数和 query 里面的进行合并
        all_query = sorted(query + url_query)
        url_with_query = url_without_query + "?" + urllib.parse.urlencode(all_query)

        body = request_obj.body
        if body:
            str_body = str(sorted(list(body.items())))
            data = url_with_query + method + str_body
        else:
            data = url_with_query + method
        # print(data)
        return data

    def is_exist(self, request_obj: Request):
        """
        判断请求是否已经处理过
        :param request_obj:
        :return:
        """
        data = self.get_request_filter_data(request_obj)
        # print(data)
        return self.filter_obj.is_exist(data)

    def mark_request(self, request_obj):
        """
        标记已经处理过的请求对象 即将这个数据保存到过滤器中
        下次再出现的时候就不会将这个请求再次纳入
        :param request_obj:
        :return:
        """
        data = self.get_request_filter_data(request_obj)
        self.filter_obj.save(data)


if __name__ == "__main__":
    q = RequestFilter(None)
    q.get_request_filter_data(Request("https://www.baidu.com/s?wd=python", query={"name": "ruiyang"}))
    q.get_request_filter_data(Request("https://www.baidu.com/s", query={"name": "ruiyang"}))
    q.get_request_filter_data(Request("https://www.baidu.com/s"))

    # 创建一个基于内存的过滤器
    filter_obj = get_filter_class("memory")()

    # 基于该过滤器创建一个请求过滤器
    request_filter = RequestFilter(filter_obj)

    # 创建一些示例请求
    r1 = Request(name="r1", url="https://www.baidu.com/s?wd=python")
    r2 = Request(name="r2", url="https://www.baidu.com/s?wd=python", query={"name": "ruiyang"})
    r3 = Request(name="r3", url="https://www.baidu.com/s", query={"name": "ruiyang", "wd": 'python'})
    r4 = Request(name="r4", url="HTTPS://www.baidu.com/s?wd=python")
    r5 = Request(name="r5", url="HTTPS://www.baidu.com/s?wd=python", query={"name": "kailun"})

    rs = [r1, r2, r3, r4, r5]

    for r in rs:
        if request_filter.is_exist(r):
            print("重复请求{}".format(r))
        else:
            request_filter.mark_request(r)
            print("标记请求{}".format(r))
