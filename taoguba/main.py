import math
import sys

sys.path.append("./../")
from taoguba.tgb import TaogubaSpider

"""
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/tgb:v0.0.1 .
docker run -itd --name tgb registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/tgb:v0.0.1
"""

if __name__ == "__main__":
    t = TaogubaSpider()
    # # 将全部的列表页 url 采集到 mongodb 数据库中
    all_keys = sorted(list(t.lowerkeys.items()))
    # print(len(all_keys))  # 3919

    group_length = math.ceil(len(all_keys) / 500)
    # print(group_length)  # 8
    t.start_requests(dict(all_keys[15:]))

    sys.exit(0)

    def spider(keys):
        TaogubaSpider().start_requests(keys)


    with ThreadPoolExecutor(max_workers=5) as t:  # 创建一个最大容纳数量为5的线程池

        task1 = t.submit(spider, dict(all_keys[:800]))  # 通过submit提交执行的函数到线程池中
        task2 = t.submit(spider, dict(all_keys[800:1600]))
        task3 = t.submit(spider, dict(all_keys[1600:2400]))
        task4 = t.submit(spider, dict(all_keys[2400:3200]))
        task5 = t.submit(spider, dict(all_keys[3200:]))

        # print(f"task1: {task1.done()}")  # 通过done来判断线程是否完成
        time.sleep(2.5)
        # print(f"task1: {task1.done()}")
        print(task1.result())  # 通过result来获取返回值
        print(task2.result())  # 通过result来获取返回值
        print(task3.result())  # 通过result来获取返回值
        print(task4.result())  # 通过result来获取返回值
        print(task5.result())  # 通过result来获取返回值