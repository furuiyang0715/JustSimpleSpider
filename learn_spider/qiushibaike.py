# import requests
# from lxml import html
# import json
#
#
# class QiuBaiSpider(object):
#     """嗅事百科爬虫
#     需求: 提取糗百中热门主题中所有段子信息,每个段子包含发送人头像URL,昵称,性别,段子内容, 好笑数,评论数
#     """
#     def __init__(self):
#         self.url_pattern = "https://www.qiushibaike.com/8hr/page/{}/"
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
#         }
#
#     def get_url_list(self):
#         """要爬取的url列表页"""
#         return [self.url_pattern.format(i) for i in range(1, 14)]
#
#     def get_html(self, url):
#         """获取要爬取的页面的 content 信息"""
#         response = requests.get(url, headers=self.headers)
#         return response.content
#
#     def get_content_list(self, text):
#         doc = html.fromstring(text)
#         # //*[@id="content"]/div/div[2]/div
#         lis = doc.xpath(".//div[@class='recommend-article']/ul/li")
#         # print(lis)     # 发送人头像URL,昵称,性别,段子内容, 好笑数,评论数
#         '''
#         <li class="item typs_video" id="qiushi_tag_123269490">
#             <a class="recmd-left video" href="/article/123269490" rel="nofollow" target="_blank" onclick="_hmt.push(['_trackEvent','web-list-video','chick'])">
#                 <img src="//qiubai-video-web.qiushibaike.com/51SN0556L0Z1U930_hd.jpg?imageView2/1/w/150/h/112" alt="糗友们，这个怎么说？">
#                 <div class="recmd-tag">0:11</div>
#             </a>
#             <div class="recmd-right">
#                 <a class="recmd-content" href="/article/123269490" target="_blank" onclick="_hmt.push(['_trackEvent','web-list-user','chick'])">糗友们，这个怎么说？</a>
#                 <div class="recmd-detail clearfix">
#                     <div class="recmd-num">
#                         <span>211</span>
#                         <span>好笑</span>
#                         <span>·</span>
#                         <span>2</span>
#                         <span>评论</span>
#                     </div>
#
#                     <a class="recmd-user">
#                         <img src="//pic.qiushibaike.com/system/avtnew/4408/44087374/thumb/20200611150249.jpg?imageView2/1/w/50/h/50" alt="缘来～是你啊">
#                         <span class="recmd-name">缘来～是...</span>
#                     </a>
#                 </div>
#             </div>
#         </li>
#         '''
#         for li in lis:
#             # 发送人头像URL
#             user_img = li.xpath(".//a[@class='recmd-user']/img/@src")[0].lstrip("//")
#             print(user_img)
#             # 昵称
#             user_name = li.xpath(".//span[@class='recmd-name']")[0].text_content()
#             print(user_name)
#             # 性别
#             # 段子内容
#             title = li.xpath(".//a[@class='recmd-content']")[0].text_content()
#             print(title)
#             # 好笑数
#             read_info = li.xpath(".//div[@class='recmd-num']/span")
#             vote = int(read_info[0].text_content())
#             comments = int(read_info[-2].text_content())
#             print(vote)
#             print(comments)
#             # 评论数
#
#     def run(self):
#         url_list = self.get_url_list()
#         print(url_list)
#         for url in url_list:
#             print(url)
#             html = self.get_html(url)
#             text = html.decode()
#             content_list = self.get_content_list(text)


import requests
from lxml import etree
import json
from queue import Queue
import threading

'''
1. 创建 URL队列, 响应队列, 数据队列 在init方法中
2. 在生成URL列表中方法中,把URL添加URL队列中
3. 在请求页面的方法中,从URL队列中取出URL执行,把获取到的响应数据添加响应队列中
4. 在处理数据的方法中,从响应队列中取出页面内容进行解析, 把解析结果存储数据队列中
5. 在保存数据的方法中, 从数据队列中取出数据,进行保存
6. 开启几个线程来执行上面的方法
'''


def run_forever(func):
    def wrapper(obj):
        while True:
            func(obj)
    return wrapper


class QiubaiSpider(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
        }
        self.url_pattern = 'https://www.qiushibaike.com/8hr/page/{}/'
        # url 队列
        self.url_queue = Queue()
        # 响应队列
        self.page_queue = Queue()
        # 数据队列
        self.data_queue = Queue()

    def add_url_to_queue(self):
        for i in range(1, 14):
            self.url_queue.put(self.url_pattern.format(i))

    @run_forever
    def add_page_to_queue(self):
        ''' 发送请求获取数据 '''
        url = self.url_queue.get()
        # print(url)
        response = requests.get(url, headers=self.headers)
        print(response.status_code)
        if response.status_code != 200:
            self.url_queue.put(url)
        else:
            self.page_queue.put(response.content)
        # 完成当前URL任务
        self.url_queue.task_done()

    @run_forever
    def add_dz_to_queue(self):
        '''根据页面内容使用lxml解析数据, 获取段子列表'''
        page = self.page_queue.get()
        # print(page)
        element = etree.HTML(page)
        # 先分组,获取分组列表
        div_s = element.xpath('//*[@id="content-left"]/div')
        # 遍历分组列表, 再使用xpath获取内容
        dz_list = []
        for div in div_s:
            item = {}
            # 每个段子包含发送人头像URL, 昵称, 性别, 段子内容, 好笑数,评论数
            # 头像URL
            item['head_url'] = self.get_first_element(div.xpath('./div[1]/a[1]/img/@src'))
            if item['head_url'] is not None:
                item['head_url'] = 'http:' + item['head_url']

                # 昵称
            item['author_name'] = self.get_first_element(div.xpath('./div[1]/a[2]/h2/text()'))
            # 性别
            gender_class = self.get_first_element(div.xpath('./div[1]/div/@class'))
            if gender_class is not None:
                item['author_gender'] = 'man' if gender_class.find('man') != -1 else 'women'
            # 段子内容
            item['dz_content'] = self.get_first_element(div.xpath('./a/div/span[1]/text()'))

            # 好笑数
            item['dz_funny'] = self.get_first_element(div.xpath('./div[2]/span[1]/i/text()'))
            # 评论数
            item['dz_comments'] = self.get_first_element(div.xpath('./div[2]/span[2]/a/i/text()'))
            # print(item
            dz_list.append(item)
        # print(dz_list)
        self.data_queue.put(dz_list)
        self.page_queue.task_done()

    def get_first_element(self, list):
        '''获取列表中第一个元素,如果是空列表就返回None'''
        return list[0] if len(list) != 0 else None

    @run_forever
    def save_dz_list(self):
        '''把段子信息保存到文件中'''
        dz_list = self.data_queue.get()
        with open('qiushi_thread.txt', 'a', encoding='utf8') as f:
            for dz in dz_list:
                json.dump(dz, f, ensure_ascii=False)
                f.write('\n')
        self.data_queue.task_done()

    def run_use_more_task(self, func, count=1):
        '''把func放到线程中执行, count:开启多少线程执行'''
        for i in range(0, count):
            t = threading.Thread(target=func)
            t.setDaemon(True)
            t.start()

    def run(self):
        # 开启线程执行上面的几个方法
        url_t = threading.Thread(target=self.add_url_to_queue)
        # url_t.setDaemon(True)
        url_t.start()

        self.run_use_more_task(self.add_page_to_queue, 3)
        self.run_use_more_task(self.add_dz_to_queue, 2)
        self.run_use_more_task(self.save_dz_list, 2)

        # 使用队列join方法,等待队列任务都完成了才结束
        self.url_queue.join()
        self.page_queue.join()
        self.data_queue.join()


if __name__ == '__main__':
    qbs = QiubaiSpider()
    qbs.run()
