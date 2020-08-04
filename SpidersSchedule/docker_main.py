# coding=utf8
import functools
import os
import pprint
import sys
import time
import traceback

import docker
import schedule

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from SpidersSchedule.daemon import Daemon
from configs import LOCAL
from base import logger, SpiderBase


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                logger.warning(traceback.format_exc())
                # sentry.captureException(exc_info=True)
                if cancel_on_failure:
                    logger.warning("异常 任务结束: {}".format(schedule.CancelJob))
                    schedule.cancel_job(job_func)
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


class DockerSwith(SpiderBase, Daemon):
    def __init__(self, *args, **kwargs):
        super(DockerSwith, self).__init__()    # init SpiderBase
        super(SpiderBase, self).__init__(*args, **kwargs)     # init Daemon
        self.tables = list()
        self.docker_client = docker.from_env()
        self.docker_containers_col = self.docker_client.containers

    def ding_crawl_information(self):
        self._spider_init()
        print(self.tables)
        msg = ''
        for table, dt_benchmark in self.tables:
            sql = '''SELECT count(id) as inc_count FROM {} WHERE {} > date_sub(CURDATE(), interval 1 day);'''.format(table, dt_benchmark)
            inc_count = self.spider_client.select_one(sql).get("inc_count")
            msg += '{} 今日新增 {}\n'.format(table, inc_count)

        if not LOCAL:
            self.ding(msg)
        else:
            print(msg)

    def show_spider_logs(self, spider_name, lines=100):
        spider_container = self.docker_containers_col.get(spider_name)
        log_info = spider_container.logs(tail=lines).decode()
        return log_info

    def clear_all(self):
        # TODO 配置化
        container_names = [
            "calendar_news",
            "dongc",
            "cls",
            "cls2",
            "gov",
            "juf",
            "juc",
            "m163",
            "qqf",
            "shcn",
            "sohu",
            "stcn",
            "tkg",
            "tgb",
            "yicai",
            "p2peye",
            'cn9666',
            'cctv',

        ]
        for name in container_names:
            try:
                spider_container = self.docker_containers_col.get(name)
            except:
                spider_container = None

            if spider_container:
                spider_container.remove(force=True)

    def docker_run_spider(self, spider_name, spider_file_path, restart=False):
        local_int = 1 if LOCAL else 0
        try:
            spider_container = self.docker_containers_col.get(spider_name)
        except:
            spider_container = None

        if spider_container:
            spider_status = spider_container.status
            logger.info("{} spider status: {}".format(spider_name, spider_status))
            if spider_status in ("exited",):
                spider_container.start()
            elif spider_status in ("running",):
                if restart:
                    spider_container.restart()
            else:
                logger.warning("other status: {}".format(spider_status))
        else:
            self.docker_containers_col.run(
                "registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spi:v1",
                environment={"LOCAL": local_int},
                name='{}'.format(spider_name),
                command='python {}'.format(spider_file_path),
                detach=True,    # 守护进程运行
            )

    def start_task(self, spider_name, spider_file_path, table_name, dt_benchmark, dt_str, restart=False):
        """
        使用定时任务每天固定时间启动 docker 进程
        :param spider_name: 爬虫名称/容器名
        :param spider_file_path: 爬虫文件路径
        :param table_name: 爬虫数据存放数据库表名
        :param dt_benchmark: 爬虫增量字段 例如 pub_date 则是以发布时间来衡量两个点之间的数据增量
        :param dt_str: 定时任务时间字符串
        :param restart: 如果前一个任务的容器还在运行 是否进行重启
        :return:
        """
        @catch_exceptions(cancel_on_failure=True)
        def task():
            self.docker_run_spider(spider_name, spider_file_path, restart)

        self.tables.append((table_name, dt_benchmark))
        schedule.every().day.at(dt_str).do(task)

    def interval_start_task(self, spider_name, spider_file_path, table_name, dt_benchmark, interval, restart=True):
        """
        使用定时任务固定间隔启动 docker 进程
        :param spider_name:
        :param spider_file_path:
        :param table_name:
        :param dt_benchmark:
        :param interval: 元组（间隔时间, 间隔单位）eg. (10, "minutes"), 每 10 分钟运行一次
        :param restart:
        :return:
        """
        @catch_exceptions(cancel_on_failure=True)
        def task():
            self.docker_run_spider(spider_name, spider_file_path, restart)

        self.tables.append((table_name, dt_benchmark))
        sche = schedule.every(interval[0])
        assert interval[1] in ('seconds', 'minutes', 'hours', 'days', 'weeks')
        sche.unit = interval[1]
        sche.do(task)

    def run(self):   # TODO 改为读取更新配置的 或许可以配合 watch dog 主动构建？
        self.clear_all()

        # 交易所日历公告爬虫 / 每天爬取 1 次
        self.docker_run_spider("calendar_news", 'CalendarNewsRelease/news_release.py')
        self.start_task("calendar_news", 'CalendarNewsRelease/news_release.py', 'calendar_news', 'PubDate', '01:00')

        # 东财财富号 / 每天爬取 1 次
        # TODO 暂定 运行完一次时间较长 升频时添加一个制动混合启动
        self.docker_run_spider("dongc", 'CArticle/ca_main.py')
        self.start_task("dongc", 'CArticle/ca_main.py', "eastmoney_carticle", 'pub_date', "02:00", restart=True)

        # 财新社
        # 财新社电报 / 每小时爬取一次
        # 财新社按照新闻编号爬取 / 每小时爬取一次
        self.docker_run_spider("cls", 'ClsCnInfo/telegraphs.py')
        self.docker_run_spider("cls2", 'ClsCnInfo/cls_details.py')
        self.interval_start_task("cls", 'ClsCnInfo/telegraphs.py', 'cls_telegraphs', 'pub_date', (1, "hours"))
        self.interval_start_task("cls2", 'ClsCnInfo/cls_details.py', 'cls_telegraphs', 'pub_date', (1, "hours"))

        # 政府新闻等 / 每天爬取一次
        self.docker_run_spider("gov", 'GovSpiders/gov_main.py')
        self.start_task("gov", 'GovSpiders/gov_main.py', 'chinabank', 'pub_date', "03:00", restart=True)

        # 巨丰财经 / 每 40 min 爬取一次
        self.docker_run_spider('juf', 'JfInfo/jfinfo_main.py')
        self.interval_start_task('juf', 'JfInfo/jfinfo_main.py', 'jfinfo', 'pub_date', (40, "minutes"))

        # 巨潮资讯 / 每 2 小时更新一次
        self.docker_run_spider('juc', 'JuchaoInfo/juchao.py')
        self.interval_start_task('juc', 'JuchaoInfo/juchao.py', "juchao_info", 'pub_date', (2, "hours"))

        # 网易财经 / 每天更新一次 （TODO 新版页面升级）
        self.docker_run_spider('m163', 'Money163/netease_money.py')
        self.start_task('m163', 'Money163/netease_money.py', "netease_money", 'pub_date', "04:00")

        # 腾讯财经 / 每 50 min 更新一次 (TODO 新版页面升级)
        self.docker_run_spider('qqf', 'QQStock/qq_stock.py')
        self.interval_start_task('qqf', 'QQStock/qq_stock.py', "qq_Astock_news", 'pub_date', (50, "minutes"))

        # 上海证券报 / 每 30 min 更新一次
        self.docker_run_spider('shcn', 'ShangHaiSecuritiesNews/cn_main.py')
        self.interval_start_task('shcn', 'ShangHaiSecuritiesNews/cn_main.py', 'cn_stock', 'pub_date', (30, "minutes"))

        # 搜狐财经 / 每 10 min 更新一次
        self.docker_run_spider('sohu', 'sohu/sohu_spider.py')
        self.interval_start_task('sohu', 'sohu/sohu_spider.py', 'SohuFinance', 'pub_date', (10, "minutes"))

        # 中国证券报 / 每 20 min 更新一次
        self.docker_run_spider('stcn', 'StockStcn/kuaixun.py')
        self.interval_start_task('stcn', 'StockStcn/kuaixun.py', "stcn_info", 'pub_date', (20, 'minutes'))

        # 大公报 / 每 25 min 更新一次
        self.docker_run_spider('tkg', 'Takungpao/takungpao_main.py')
        self.interval_start_task('tkg', 'Takungpao/takungpao_main.py', 'Takungpao', 'pub_date', (25, "minutes"))

        # 淘股吧 / 每天运行一次
        self.docker_run_spider('tgb', 'Taoguba/tgb_main.py')
        self.start_task('tgb', 'Taoguba/tgb_main.py', 'taoguba', 'pub_date', "05:00")

        # 第一财经 / 每 10 min 爬取一次
        self.docker_run_spider('yicai', 'YiCai/yicai_spider.py')
        self.interval_start_task('yicai', 'YiCai/yicai_spider.py', 'NewsYicai', 'pub_date', (10, 'minutes'))

        # 天眼网贷 / 每小时更新一次
        self.docker_run_spider('p2peye', "P2Peye/p2peyespider.py")
        self.interval_start_task('p2peye', "P2Peye/p2peyespider.py", 'p2peye_news', 'pub_date', (2, 'hours'))

        # 牛仔网 / 每 5 小时更新一次
        self.docker_run_spider('cn9666', 'CN966/9666pinglun.py')
        self.interval_start_task('cn9666', 'CN966/9666pinglun.py', '9666pinglun', 'pub_date', (5, 'hours'))

        # 央视网财经频道 / 每小时更新一次
        self.docker_run_spider('cctv', 'CCTVFinance/cctv_spider.py')
        self.interval_start_task('cctv', 'CCTVFinance/cctv_spider.py', 'cctvfinance', 'pub_date', (1, 'hours'))

        self.ding_crawl_information()
        schedule.every(2).hours.do(self.ding_crawl_information)

        while True:
            # logger.info("当前调度系统中的任务列表是:\n{}".format(pprint.pformat(schedule.jobs)))
            schedule.run_pending()
            time.sleep(10)


def main():
    DockerSwith().run()


if __name__ == "__main__":
    pid_file = os.path.join(cur_path, 'main.pid')
    log_file = os.path.join(cur_path, 'main.log')

    print(pid_file)
    print(log_file)

    worker = DockerSwith(
        pidfile=pid_file,
        stdout=log_file,
        stderr=log_file
    )

    if len(sys.argv) >= 2:
        if 'start' == sys.argv[1]:
            worker.start()
        elif 'stop' == sys.argv[1]:
            worker.stop()
        elif 'restart' == sys.argv[1]:
            worker.restart()
        elif 'status' == sys.argv[1]:
            worker.status()
        else:
            sys.stderr.write("Unknown command\n")
            sys.exit(2)
        sys.exit(0)
    else:
        sys.stderr.write("usage: %s start|stop|restart\n" % sys.argv[0])
        sys.exit(2)
