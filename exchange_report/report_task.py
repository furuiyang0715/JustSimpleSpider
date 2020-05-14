import sys
import traceback


sys.path.append("./../")
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

    task()
