import pprint
import re

import requests
from lxml import html


class STCN_YaoWen(object):
    def __init__(self):
        self.list_url = "http://news.stcn.com/"
        self.table = "stcn_info"

    def _get(self, url):
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.text

    def _parse_detail(self, body):
        doc = html.fromstring(body)
        nodes = doc.xpath("//div[@class='txt_con']/p")
        contents = []
        for node in nodes:
            contents.append(node.text_content())
        article = "".join(contents)
        return article

    def _parse_list_body(self, body):
        doc = html.fromstring(body)
        items = []
        # 题头文章
        first = doc.xpath("//dl[@class='hotNews']")[0]
        title = first.xpath("//dt/a/@title")[0]
        link = first.xpath("//dt/a/@href")[0]
        pub_date = first.xpath("//dd[@class='sj']")[0].text_content()
        pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
        first = dict()
        first['title'] = title
        first['link'] = link
        first['pub_date'] = pub_date
        detail_body = self._get(link)
        if detail_body:
            article = self._parse_detail(detail_body)
            first['article'] = article
            items.append(first)

        # 列表文章
        columns = doc.xpath("//ul[@class='news_list']/li")
        # num = 0
        for column in columns:
            # num += 1
            # print(column.tag)
            title = column.xpath("./p[@class='tit']/a/@title")[0]
            link = column.xpath("./p[@class='tit']/a/@href")[0]
            pub_date = column.xpath("./p[@class='sj']")[0].text_content()
            pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
            # print(title, link, pub_date)
            item = dict()
            item['title'] = title
            item['link'] = link
            item['pub_date'] = pub_date
            detail_body = self._get(link)
            if detail_body:
                article = self._parse_detail(detail_body)
                item['article'] = self._process_content(article)
                items.append(item)
        # print(num)
        return items

    def _filter_char(self, test_str):
        # 处理特殊的空白字符
        # '\u200b' 是 \xe2\x80\x8b
        for cha in ['\n', '\r', '\t',
                    '\u200a', '\u200b', '\u200c', '\u200d', '\u200e',
                    '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
                    ]:
            test_str = test_str.replace(cha, '')
        test_str = test_str.replace(u'\xa0', u' ')  # 把 \xa0 替换成普通的空格
        return test_str

    def _process_content(self, vs):
        # 去除 4 字节的 utf-8 字符，否则插入mysql时会出错
        try:
            # python UCS-4 build的处理方式
            highpoints = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            # python UCS-2 build的处理方式
            highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

        params = list()
        for v in vs:
            # 对插入数据进行一些处理
            nv = highpoints.sub(u'', v)
            nv = self._filter_char(nv)
            params.append(nv)
        return "".join(params)

    def _contract_sql(self, to_insert):
        ks = []
        vs = []
        for k in to_insert:
            ks.append(k)
            vs.append(to_insert.get(k))
        ks = sorted(ks)  # article,link,pub_date,title
        fields_str = "(" + ",".join(ks) + ")"
        values_str = "(" + "%s," * (len(vs) - 1) + "%s" + ")"
        base_sql = '''INSERT INTO `{}` '''.format(self.table) + fields_str + ''' values ''' + values_str + ''';'''
        # return base_sql, tuple(vs)
        return base_sql

    def _start(self):
        list_body = self._get(self.list_url)
        if list_body:
            items = self._parse_list_body(list_body)
            # print(pprint.pformat(items))
            values = [(item.get("article"),
                      item.get("link"),
                      item.get("pub_date"),
                      item.get("title")) for item in items]
            insert_many_sql = self._contract_sql(items[0])
            # print(insert_many_sql)
            # print(pprint.pformat(values))


if __name__ == "__main__":
    d = STCN_YaoWen()
    d._start()
    item = {
        'article': '证券时报e公司讯，2月16日0—24时，31个省（自治区、直辖市）和新疆生产建设兵团报告新增确诊病例2048例，新增死亡病例105例（湖北100例，河南3例，广东2例），新增疑似病例1563例。',
        'link': 'http://kuaixun.stcn.com/2020/0217/15643313.shtml',
        'pub_date': '2020-02-17 08:55',
        'title': '全国新增2048例新冠肺炎 累计报告70548例新冠肺炎'}
    # ret = d._contract_sql(item)
    # print(ret)