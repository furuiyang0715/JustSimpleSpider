"""
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/gov_stats:v0.0.1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/gov_stats:v0.0.1

redis = Redis(host='redis', port=6379)


"""
import time

import sys
sys.path.append("./..")

from national_statistics.gov_stats_zxfb import GovStats
from national_statistics.my_log import logger

if __name__ == "__main__":
    t1 = time.time()
    runner = GovStats()
    runner.start()
    logger.info("列表页爬取失败 {}".format(runner.error_list))
    logger.info("详情页爬取失败 {}".format(runner.detail_error_list))
    t2 = time.time()
    logger.info("花费的时间是 {} s".format(t2-t1))

