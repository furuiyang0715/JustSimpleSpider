import datetime
import json
import logging
import sys
# sys.path.insert(0, '/home/huangminyi/project/spider')
import threading
import time
from queue import Queue
import pymysql
import redis
import requests
from sqlalchemy import create_engine
sys.path.insert(0, '/home/huangminyi/project/spider_pycharm')
# sys.path.insert(0, 'F:\spider\spider')
from settings import host_r, password_r, port_r, MYSQL_M_UM4, MYSQL_S_XQ, LOG_FILE
LOG_FILE = LOG_FILE.format('EMLGTNanBeiXiangZiJin')
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s "#配置输出日志格式
DATE_FORMAT = '%Y-%m-%d  %H:%M:%S %a ' #配置输出时间的格式，注意月份和天数不要搞乱了
logger = logging.getLogger(__name__)


class EMLGTNanBeiXiangZiJin(object):

    def __init__(self):
        self.rel = redis.Redis(host=host_r, port=port_r, password=password_r)
        # # 测试数据库
        # self.engine = create_engine(MYSQL_M_UM4, pool_recycle=3600)
        # self.conn = pymysql.connect(user='rootb', password='3x870OV649AMSn*', host='14.152.49.155',
        #                             port=8998, charset='utf8', db='hmy')
        self.headers = {
            'Referer': 'http://data.eastmoney.com/hsgt/index.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
        }
        self.data_to_sql_queue = Queue(maxsize=0)
        logging.basicConfig(level=logging.DEBUG,
                            format=LOG_FORMAT,
                            datefmt=DATE_FORMAT,
                            filename=LOG_FILE  # 有了filename参数就不会直接输出显示到控制台，而是直接写入文件
                            )

    def get_response(self):
        try:
            time.sleep(4)
            url = 'http://push2.eastmoney.com/api/qt/kamt.rtmin/get?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55,f56&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery18306854619522421488_1566280636697&_=1566284477196'
            response = requests.get(url=url, headers=self.headers)
            # print(response.content.decode('utf8'))
            html = response.content.decode('utf8')
            return html
        except Exception as e:
            print('获取网页错误：{}'.format(e))
            logger.info('获取网页错误：{}'.format(e))

    def get_data_json(self, html):
        if html is not None:
            start_num = html.find('(')
            end_num = html.find(')')
            # print(start_num, end_num) # 40 35819
            new_html = html[start_num+1:end_num]
            # print(new_html)
            html_json = json.loads(new_html)
            # print(html_json)
        else:
            html_json = None
        return html_json

    @staticmethod
    def da_lis(da_lis):
        d_lis = []
        for da in da_lis:
            if da == '-':
                da = da.replace('-', '0')
                d_lis.append(da)
            else:
                d_lis.append(da)
        return d_lis

    def processing_s2n_data(self, html_json):
        # s2n --- 北向资金
        # n2s --- 南向资金
        # 's2nDate': '08-20', 'n2sDate': '08-20'
        # print(html_json)
        if html_json:
            item = {}
            s2n_date = html_json['data']['s2nDate']
            s2n_data = html_json['data']['s2n']
            now = datetime.datetime.now().strftime('%Y')
            for da in s2n_data:
                da_lis = da.split(',')
                # print(da_lis)
                da_lis = self.da_lis(da_lis)
                time = da_lis[0]
                item['Date'] = now + '-' + s2n_date + ' ' + time
                item['SHFlow'] = da_lis[1]
                item['SHBalance'] = da_lis[2]
                item['SZFlow'] = da_lis[3]
                item['SZBalance'] = da_lis[4]
                item['NorthMoney'] = da_lis[5]
                item['Category'] = '北向资金'
                # print(item)
                # 比较时间
                time_before = (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M')
                time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                Nine_Ten_Now = datetime.datetime.now().strftime('%H%M%S')
                # print(time_now[11:])
                # if 90000 < int(Nine_Ten_Now) < 100000:
                if 100000 < int(Nine_Ten_Now) < 110000:
                    # 9点到10点
                    # print(11111111111111111111111111111)
                    self.data_to_sql_queue.put(item)
                    self.save_data()
                elif time_now[13:] == ':30':
                    # print('000000000000000000000000000000000')
                    self.data_to_sql_queue.put(item)
                    self.save_data()
                else:
                    if time_now >= item['Date'] >= time_before:
                        print(item['Date'])
                        self.data_to_sql_queue.put(item)
                        self.save_data()
        else:
            print('数据没有获取到')
            # 入库

    def processing_n2s_data(self, html_json):
        # s2n --- 北向资金
        # n2s --- 南向资金
        # 's2nDate': '08-20', 'n2sDate': '08-
        if html_json:
            item = {}
            n2s_date = html_json['data']['n2sDate']
            n2s_data = html_json['data']['n2s']
            now = datetime.datetime.now().strftime('%Y')
            for da in n2s_data:
                da_lis = da.split(',')
                # print(da_lis)
                da_lis = self.da_lis(da_lis)
                time = da_lis[0]
                item['HKHFlow'] = da_lis[1]
                item['HKHBalance'] = da_lis[2]
                item['HKZFlow'] = da_lis[3]
                item['HKZBalance'] = da_lis[4]
                item['SouthMoney'] = da_lis[5]
                item['Date'] = now + '-' + n2s_date + ' ' + time
                item['Category'] = '南向资金'
                # print(item)
                # 比较时间
                time_before = (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M')
                time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                Nine_Ten_Now = datetime.datetime.now().strftime('%H%M%S')
                # print(time_now, time_before, item['Date'])
                if 90000 < int(Nine_Ten_Now) < 100000:
                    # 9点到10点
                    self.data_to_sql_queue.put(item)
                    self.save_data()
                elif time_now[13:] == ':30':
                    self.data_to_sql_queue.put(item)
                    self.save_data()
                else:
                    if time_now >= item['Date'] >= time_before:
                        print(item['Date'])
                        self.data_to_sql_queue.put(item)
                        self.save_data()
        else:
            print('没有获取到信息')

    def save_data(self):
        while not self.data_to_sql_queue.empty():
            item = self.data_to_sql_queue.get()
            if item['Category'] == '北向资金':
                sql1 = """
                    INSERT INTO lgt_north_money_data(SHFlow, SHBalance, SZFlow, SZBalance, NorthMoney, Category, Date) 
                    values ('{}','{}','{}','{}','{}','{}','{}') on duplicate key update SHFlow='{}',SHBalance='{}',
                    SZFlow='{}',SZBalance='{}',NorthMoney='{}', Category='{}',Date='{}';
                                                                                """
                sql_x = sql1.format(item['SHFlow'], item['SHBalance'], item['SZFlow'], item['SZBalance'],
                                    item['NorthMoney'], item['Category'], item['Date'],
                                    item['SHFlow'], item['SHBalance'], item['SZFlow'], item['SZBalance'],
                                    item['NorthMoney'], item['Category'], item['Date']
                                    )
            else:
                sql1 = """
                    INSERT INTO lgt_south_money_data(HKHFlow, HKHBalance, HKZFlow, HKZBalance, SouthMoney, Category, Date) 
                    values ('{}','{}','{}','{}','{}','{}','{}') on duplicate key update HKHFlow='{}',HKHBalance='{}',
                    HKZFlow='{}',HKZBalance='{}',SouthMoney='{}', Category='{}',Date='{}';
                                                                                            """
                sql_x = sql1.format(item['HKHFlow'], item['HKHBalance'], item['HKZFlow'], item['HKZBalance'],
                                    item['SouthMoney'], item['Category'], item['Date'],
                                    item['HKHFlow'], item['HKHBalance'], item['HKZFlow'], item['HKZBalance'],
                                    item['SouthMoney'], item['Category'], item['Date']
                                    )
            conn = pymysql.connect(user='{}'.format(MYSQL_S_XQ['user_s']),
                                        password='{}'.format(MYSQL_S_XQ['password_s']),
                                        host='{}'.format(MYSQL_S_XQ['host_s']),
                                        port=MYSQL_S_XQ['port_s'],
                                        charset='{}'.format(MYSQL_S_XQ['charset_s_utf8']),
                                        db='{}'.format(MYSQL_S_XQ['db_s']))
            cur = conn.cursor()
            try:
                conn.ping(reconnect=True)
                cur.execute(sql_x)
                conn.commit()
                print("成功入库-----------")
                logger.info(item)
                logger.info('成功入库-----------')
            except Exception as e:
                conn.ping(reconnect=True)
                conn.rollback()
                # print(item['Content'], item['Category'])
                print("入库失败,原因是{},发生回滚".format(e))
            cur.close()
            conn.close()

    def run(self):
        # 入口
        html = self.get_response()
        html_json = self.get_data_json(html)
        if html_json is not None:
            ts2n = threading.Thread(target=self.processing_s2n_data, args=(html_json,))
            tn2s = threading.Thread(target=self.processing_n2s_data, args=(html_json,))
            ts2n.start()
            tn2s.start()
            ts2n.join()
            tn2s.join()
        # 程序结束后


if __name__ == '__main__':
    i = 0
    time_total = 0
    time_s = 5
    while True:
        t1 = time.time()
        lg = EMLGTNanBeiXiangZiJin()
        lg.run()
        t = time.time()-t1
        print(t)
        logger.info(t)
        t_t = t + time_s
        time_total += t_t
        i += 1
        time.sleep(time_s)
        if i > 3:
            break
        if 60 - time_total <= 10:
            break

    # time_sleep = 5
    # i = 0
    # while True:
    #     t1 = time.time()
    #     lg = EMLGTNanBeiXiangZiJin()
    #     lg.run()
    #     t = time.time()-t1
    #     print(t)
    #     time.sleep(time_sleep)
    #     i += time_sleep
    #     if 60 - i <= 10:
    #         break

