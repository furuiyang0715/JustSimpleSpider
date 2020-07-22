'''
参考： https://docker-py.readthedocs.io/en/stable/index.html
安装： pip install docker



'''
import pprint
import sys
import threading
import time
import docker


def create_docker_client():
    # 创建 docker python 客户端
    # docker_client = docker.from_env()
    docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    docker_version_info = docker_client.version()
    # 查看 docker 的版本信息
    print(pprint.pformat(docker_version_info))
    # 查看 docker 的内存占用信息
    docker_df_info = docker_client.df()
    # print(pprint.pformat(docker_df_info))


def monite_docker_events():
    docker_client = docker.from_env()
    docker_events = docker_client.events()

    def monitor():
        for event in docker_events:
            print(event)

    threading.Thread(target=monitor).start()
    time.sleep(50)
    docker_events.close()


monite_docker_events()

sys.exit(0)

docker_containers_col = docker_client.containers
# print(docker_containers_col)

docker_containers = docker_containers_col.list(all=True)
# print(docker_containers)

one_container = docker_containers_col.get("e1a0c764a8")
# print(one_container)

one_container_attrs = one_container.attrs
# print(pprint.pformat(one_container_attrs))
its_image = one_container_attrs['Config']['Image']
# print(its_image)

one_container_logs = one_container.logs()
# print(one_container_logs.decode())

# one_container.start()
#
# time.sleep(10)
# one_container.stop()

docker_images_col = docker_client.images
# print(docker_images_col)
# docker_images = docker_images_col.list(all=True)
docker_images = docker_images_col.list()
# print(len(docker_images))
