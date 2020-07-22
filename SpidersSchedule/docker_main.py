import traceback

import docker

docker_client = docker.from_env()


def docker_run_spider(spider_name, spider_file_path):
    docker_containers_col = docker_client.containers
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
