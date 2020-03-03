import threadpool


from PublicOpinion.jfinfo.hk_info import HKInfo
from PublicOpinion.jfinfo.reference import Reference
from PublicOpinion.jfinfo.research import Research
from PublicOpinion.jfinfo.tzzjy import TZZJY


class JFSchedule(object):

    def ins_start(self, instance):
        instance.start()

    def start(self):
        class_lst = [
            HKInfo,    # 港股资讯
            Reference,  # 巨丰内参
            Research,  # 巨丰研究院
            TZZJY,  # 投资者教育
        ]

        # instance 列表
        ins_list = [cls() for cls in class_lst]

        pool = threadpool.ThreadPool(4)
        reqs = threadpool.makeRequests(self.ins_start, ins_list)
        [pool.putRequest(req) for req in reqs]
        pool.wait()


if __name__ == "__main__":

    sche = JFSchedule()
    sche.start()
