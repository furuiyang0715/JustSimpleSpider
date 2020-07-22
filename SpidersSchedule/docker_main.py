import traceback

import docker

from base import logger
from configs import LOCAL

docker_client = docker.from_env()


def docker_run_spider(spider_name, spider_file_path, restart=False):
    docker_containers_col = docker_client.containers
    # 查询该名称容器是否存在
    spider_container = docker_containers_col.get(spider_name)
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
            environment={"LOCAL": LOCAL},
            name=f'{spider_name}',
            command=f'python {spider_file_path}',
            detach=True,
        )


def main():
    docker_run_spider("test_sohu", 'sohu/sohu_spider.py')



    pass


if __name__ == "__main__":
    main()
