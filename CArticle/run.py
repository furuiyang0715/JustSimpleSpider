# import logging
# import random
# import time
#
# import pymysql
# import os
# from apscheduler.schedulers.blocking import BlockingScheduler
#
# from CArticle.spider import CArticleSpiser
# from PublicOpinion.carticle.configs import DC_HOST, DC_PORT, DC_USER, DC_PASSWD, DC_DB
#
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
#
# _now = lambda: time.time()
#
#
# class Schedule(object):
#     def __init__(self):
#         self.keys = list(self.dc_info().values())
#         random.shuffle(self.keys)
#
#     def dc_info(self):  # eg. {'300150.XSHE': '世纪瑞尔',
#         """
#         从 datacanter.const_secumain 数据库中获取当天需要爬取的股票信息
#         返回的是 股票代码: 中文名简称 的字典的形式
#         """
#         try:
#             conn = pymysql.connect(host=DC_HOST, port=DC_PORT, user=DC_USER,
#                                    passwd=DC_PASSWD, db=DC_DB)
#         except Exception as e:
#             raise
#
#         cur = conn.cursor()
#         cur.execute("USE datacenter;")
#         cur.execute("""select SecuCode, ChiNameAbbr from const_secumain where SecuCode \
#             in (select distinct SecuCode from const_secumain);""")
#         dc_info = {r[0]: r[1] for r in cur.fetchall()}
#         cur.close()
#         conn.close()
#         return dc_info
#
#     def start(self, key):
#         c = CArticleSpiser(key=key)
#         c.start()
#
#     def run(self):
#         start_time = _now()
#         for key in self.keys:
#             logger.info("当前的主题是: {}".format(key))
#             self.start(key)
#         logger.info("一次共用时: {}".format(_now() - start_time))
#
#
# def task():
#     sche = Schedule()
#     sche.run()
#
#
# if __name__ == '__main__':
#     scheduler = BlockingScheduler()
#     task()
#     scheduler.add_job(task, 'interval', hours=15)
#     logger.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
#
#     try:
#         scheduler.start()
#     except (KeyboardInterrupt, SystemExit):
#         pass
#
#
#
# '''
# docker build -f Dockerfile.carticle -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1 .
# docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1
# sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1
# sudo docker run -itd --name dongc --env LOCAL=0 registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1
#
# SELECT count(id) FROM  eastmoney_carticle  WHERE pub_date > date_sub(CURDATE(), interval 1 day);
# '''
