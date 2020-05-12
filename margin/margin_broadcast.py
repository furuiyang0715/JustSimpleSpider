"""post 公告接口"""
import datetime
import json
import random
import re
import sys
from urllib.parse import urljoin

import requests
from lxml import html

from margin.base import MarginBase


class MarginBroadcast(MarginBase):
    def __init__(self):
        super(MarginBroadcast, self).__init__()
        # sh
        self.sh_url = 'http://www.sse.com.cn/disclosure/magin/announcement/s_index.htm'
        self.sh_base_url = 'http://www.sse.com.cn/disclosure/magin/announcement/s_index_{}.htm'
        self.dt_format = "%Y-%m-%d"
        self.error_urls = []

        # sz
        self.sz_url = 'http://www.szse.cn/api/search/content?random={}'.format(random.random())
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '85',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'www.szse.cn',
            'Origin': 'http://www.szse.cn',
            'Pragma': 'no-cache',
            'Referer': 'http://www.szse.cn/disclosure/margin/business/index.html',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'X-Request-Type': 'ajax',
            'X-Requested-With': 'XMLHttpRequest',
        }

        self.announcement_table = 'margin_announcement'

    def _make_sz_params(self, page_num):
        '''
        keyword:
        time: 0
        range: title
        channelCode[]: business_news
        currentPage: 1
        pageSize: 20
        '''
        datas = {
            "keyword": '',
            'time': '',
            'range': 'title',
            'channelCode[]': 'business_news',
            'currentPage': page_num,
            'pageSize': 20,
        }
        return datas

    def sz_start(self):
        for page in range(1, 8):
            datas = self._make_sz_params(page)
            resp = requests.post(self.sz_url, headers=self.headers, data=datas)
            # print(resp)
            if resp.status_code == 200:
                ret = resp.text
                py_ret = json.loads(ret)
                announcements = py_ret.get("data")
                for a in announcements:
                    print(a)
                    item = {}
                    item['title'] = a.get("doctitle")
                    item['link'] = a.get("docpuburl")
                    item['time'] = a.get('docpubtime')
                    # eg. http://www.szse.cn/disclosure/notice/general/t20200430_576647.json
                    content_json_url = urljoin("http://www.szse.cn", a.get("docpubjsonurl"))



            sys.exit(0)

    def _process_content(self, vs):
        """
        去除 4 字节的 utf-8 字符，否则插入 mysql 时会出错
        :param vs:
        :return:
        """
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
            if nv.strip():     # 不需要在字符串之间保留空格
                params.append(nv)
        # print(params)
        return "".join(params)

    def _filter_char(self, _str):
        """处理特殊的空白字符"""
        for cha in ['\n', '\r', '\t',
                    '\u200a', '\u200b', '\u200c', '\u200d', '\u200e',
                    '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
                    ]:
            _str = _str.replace(cha, '')
        # _str = _str.replace(u'\xa0', u' ')  # 把 \xa0 替换成普通的空格
        _str = _str.replace(u'\xa0', u'')  # 把 \xa0 直接去除
        return _str

    def start(self):
        for page in range(1, 23):
            if page == 1:
                url = self.sh_url
            else:
                url = self.sh_base_url.format(page)
            self.post_sh(url)

    def post_sh(self, url):
        resp = requests.post(url)
        if resp.status_code == 200:
            body = resp.text
            try:
                body = body.encode("ISO-8859-1").decode("utf-8")
            except:
                self.error_urls.append(url)
            doc = html.fromstring(body)
            '''
            <dd>
                 <span>2020-04-30</span>
                 <a href="/disclosure/magin/announcement/ssereport/c/c_20200430_5085195.shtml" title="关于融资融券标的证券调整的公告" target="_blank">关于融资融券标的证券调整的公告 </a>
            </dd>
            '''
            broadcasts = doc.xpath(".//div[@class='sse_list_1 js_createPage']/dl/dd")
            for b in broadcasts:
                item = dict()

                show_dt_str = b.xpath("./span")[0].text_content()
                show_dt = datetime.datetime.strptime(show_dt_str, self.dt_format)
                item['time'] = show_dt

                href = b.xpath("./a/@href")[0]
                # http://www.sse.com.cn/   disclosure/magin/announcement/ssereport/c/c_20200430_5085195.shtml
                href = urljoin("http://www.sse.com.cn/", href)
                item['link'] = href

                if href.endswith(".pdf") or href.endswith(".doc"):
                    item['content'] = ''
                    item['keyword'] = ''
                else:
                    ret = self.parse_sh_detail(href)
                    content = ret.get("content")
                    keyword = ret.get("keyword")
                    item['content'] = content
                    item['keyword'] = keyword

                print(item)
                # TODO 暂时的想法是将其存入 mongo 中

    def parse_sh_detail(self, url):
        """
        eg. http://www.sse.com.cn/disclosure/magin/announcement/ssereport/c/c_20200430_5085195.shtml
        :param url:
        :return:
        """
        resp = requests.get(url)
        if resp.status_code == 200:
            body = resp.text
            try:
                body = body.encode("ISO-8859-1").decode("utf-8")
            except:
                self.error_urls.append(url)

            # print(body)

            # 文章正文
            '''
            <div class="allZoom">  
                <p style="text-align: center;">上证公告（交易）〔2020〕007号</p>
                <p>　　2020年5月6日，美都能源（600175）、六国化工（600470）、飞乐音响（600651）、安信信托（600816）和宜华生活（600978）被实施退市风险警示。根据《上海证券交易所融资融券交易实施细则》第三十一条规定，本所于2020年5月6日起将以上证券调出融资融券标的证券名单。</p>
                <p>　　特此公告。<br />&nbsp;</p>
                <p>　　上海证券交易所</p>
                <p>　　2020年4月30日</p>
            </div> 
            或者: 
            
            <div class="article-infor">
                <h2>关于融资融券标的证券调整的公告</h2>
                
                <div class="article_opt">
                    <span class="js_output_apphide">
                        <a href="##" class="js_myCollection sseicon2-icon_nocollection"></a>
                        <a href="javascript:window.print();" class="mobile_hide sseicon-icon_print"></a>
                        <a href="##" class="zoom sseicon-icon_fontSizeUp" data-type="zoom_in"></a>
                        <a href="##" class="zoom sseicon-icon_fontSizeDown" data-type="zoom_out"></a>
                    </span>
                    <i> 2013-04-26</i>
                </div>
                
                <p>　　2013年5月2日，中达股份（证券代码：600074）被实施退市风险警示。根据《上海证券交易所融资融券交易实施细则》第二十九条规定，本所于2013年5月2日起将该证券调出融资融券标的证券名单。<br />&nbsp;</p>
                <p>　　特此公告。<br />&nbsp;</p>
                <p>　　上海证券交易所</p>
                <p>　　2013年4月26日</p>
                
                <div class="share js_output_apphide">分享：
                    <span>
                        <a href="javascript:void(0);" class="sinaico"> </a>
                        <a href="javascript:void(0);" class="wechatico">
                            <div class="feedback_slide" id="article_qrcode"><s></s><
                                span class="qrcode_details">微信扫一扫，分享好友</span>
                            </div>
                        </a>
                        <a href="javascript:void(0);" class="tencentico"> </a>
                    </span>
                </div>
            
            </div>
            '''
            doc = html.fromstring(body)
            try:
                # TODO 对 content 进行去噪处理
                content = doc.xpath("//div[@class='allZoom']")[0].text_content()
            except:
                content = ''

            if not content:
                try:
                    content = doc.xpath("//div[@class='article-infor']")[0].text_content()
                except:
                    content = ''

            if content:
                content = self._process_content(content)

            # 提取本篇的关键词
            '''
            <p style="display:none">
                <fjtignoreurl>
                    <span  id="searchTitle">
                        关于融资融券标的证券调整的公告
                    </span>
                    <span  id="keywords">
                            600978,
                            600816,
                            600651,
                            600470,
                            600175,
                            融资融券标的证券调整,
                    </span>
                </fjtignoreurl>
            </p>
            '''
            try:
                key_words = doc.xpath("//span[@id='keywords']")[0].text_content().split()
                words = []
                for word in key_words:
                    word = word.strip(",")
                    words.append(word)
                words_str = ','.join(words)
            except:
                words_str = ''

            # print(">>> ", content)
            # print(">>>> ", words_str)
            return {"content": content, "keyword": words_str}


if __name__ == "__main__":
    m = MarginBroadcast()
    # m.start()
    # print(m.error_urls)

    # demo_detail_url = 'http://www.sse.com.cn/disclosure/magin/announcement/ssereport/c/c_20150911_3983844.shtml'
    # m.parse_sh_detail(demo_detail_url)

    # sz
    m.sz_start()
