# 构建一个请求对象


class Request(object):
    def __init__(self, url, name=None, method='GET', query=None, body=None):
        """
        构建请求对象
        :param url:
        :param name:
        :param method:
        :param query:
        :param body:
        """
        self.url = url
        self.name = name
        self.method = method
        self.query = query
        self.body = body
