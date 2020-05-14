import os
import sys
import traceback

from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append("./../")
from exchange_report.base import logger
from exchange_report.sh_report import SHReport
from exchange_report.sz_report import SZReport


def task():
    sh_runner = SHReport()
    sz_runner = SZReport()

    try:
        sh_runner.start()
        sz_runner.start()
        msg = sh_runner.select_count() + '\n' + sz_runner.select_count()
    except Exception as e:
        traceback.print_exc()
        sh_runner.ding("行情数据爬取失败:  {}".format(e))
    else:
        sh_runner.ding(msg)


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    task()

    # 15:02, 15:50, 8:00
    scheduler.add_job(task, 'cron', hour='8, 15', min='2, 50',  max_instances=10, id="task")
    logger.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        logger.info(f"本次任务执行出错{e}")
        sys.exit(0)
