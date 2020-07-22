import os
import sys
import traceback

import docker

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from base import logger
docker_client = docker.from_env()
docker_containers_col = docker_client.containers


def docker_run_spider(spider_name, spider_file_path, restart=False):
    # 查询该名称容器是否存在
    try:
        spider_container = docker_containers_col.get(spider_name)
    except:
        spider_container = None

    if spider_container:
        # 查看其运行状态
        spider_status = spider_container.status
        logger.info(f"{spider_name} spider status: {spider_status}")
        if spider_status in ("exited", ):
            spider_container.start()
        elif spider_status in ("running", ):
            if restart:
                spider_container.restart()
        else:
            logger.warning(f"other status: {spider_status}")
    else:
        docker_containers_col.run(
            "registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spi:v1",
            environment={"LOCAL": 1},
            name=f'{spider_name}',
            command=f'python {spider_file_path}',
            detach=True,
        )


def show_spider_logs(spider_name, lines=100):
    spider_container = docker_containers_col.get(spider_name)
    log_info = spider_container.logs(tail=lines).decode()
    # print(log_info)
    return log_info


def main():
    # docker_run_spider("test_sohu", 'sohu/sohu_spider.py')
    # docker_run_spider("calander_news", 'CalendarNewsRelease/news_release.py')
    docker_run_spider("dongc", 'CArticle/ca_main.py')


    pass


if __name__ == "__main__":
    main()
