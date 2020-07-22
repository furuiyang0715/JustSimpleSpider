import traceback

import docker

from base import logger

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
            logger.info("任务已完成")
            try:
                spider_container.start()
            except:
                traceback.print_exc()
        elif spider_status in ("running", ):
            logger.info("上次任务还未执行完")
            if restart:
                try:
                    spider_container.restart()
                except:
                    traceback.print_exc()
        else:
            logger.warning(f"其他状态 {spider_status}")
    else:
        try:
            docker_containers_col.run(
                "registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spi:v1",
                environment={"LOCAL": 1},
                name=f'{spider_name}',
                command=f'python {spider_file_path}',
                detach=True,
            )
        except:
            traceback.print_exc()


def main():
    docker_run_spider("test_sohu", 'sohu/sohu_spider.py')



    pass


if __name__ == "__main__":
    main()
