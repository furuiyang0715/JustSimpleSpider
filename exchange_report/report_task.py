import os
import sys
import traceback

from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append("./../")
from exchange_report.configs import LOCAL
from exchange_report.base import logger
from exchange_report.sh_report import SHReport
from exchange_report.sz_report import SZReport


def task():
    sh_runner = SHReport()
    sz_runner = SZReport()
    local_str = "本地" if LOCAL else "远程"

    try:
        sh_runner.start()
        sz_runner.start()
        msg = "{} >> 交易所行情: ".format(local_str) + sh_runner.select_count() + '\n' + sz_runner.select_count()
    except Exception as e:
        traceback.print_exc()
        sh_runner.ding("行情数据爬取失败:  {}".format(e))
    else:
        sh_runner.ding(msg)


def task_history():
    sz_runner = SZReport()
    sz_runner.get_history_datas()


if __name__ == "__main__":
    task_history()


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    task()

    # 15:02, 15:50, 8:00
    scheduler.add_job(task, 'cron', hour='8, 15', minute='2, 50',  max_instances=10, id="task")
    logger.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        logger.info(f"本次任务执行出错{e}")
        sys.exit(0)

'''部署
docker build -f Dockerfile_report -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/exchange_report:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/exchange_report:v1 
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/exchange_report:v1

# remote 
sudo docker run --log-opt max-size=10m --log-opt max-file=3 -itd \
--env LOCAL=0 \
--name report_task \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/exchange_report:v1

# local
sudo docker run --log-opt max-size=10m --log-opt max-file=3 -itd \
--env LOCAL=1 \
--name report_task \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/exchange_report:v1

'''
