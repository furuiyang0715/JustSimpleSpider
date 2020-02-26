import traceback

import threadpool

import sys
sys.path.append("./../../")

from PublicOpinion.stcn.bankuai import STCN_BanKuai
from PublicOpinion.stcn.chuangtou import STCN_ChuangTou
from PublicOpinion.stcn.company import STCN_Company
from PublicOpinion.stcn.dapan import STCN_DaPan
from PublicOpinion.stcn.djsj import STCN_DJSJ
from PublicOpinion.stcn.finance import STCN_Finance
from PublicOpinion.stcn.gsdt import STCN_GSDT
from PublicOpinion.stcn.guonei import STCN_GuoNei
from PublicOpinion.stcn.haiwai import STCN_HaiWai
from PublicOpinion.stcn.kandianshuju import STCN_KanDianShuJu
from PublicOpinion.stcn.kcb import STCN_KCB
from PublicOpinion.stcn.kuaixun import STCN_Kuaixun
from PublicOpinion.stcn.market import STCN_Market
from PublicOpinion.stcn.renwu import STCN_RenWu
from PublicOpinion.stcn.roll import STCN_Roll
from PublicOpinion.stcn.sbdt import STCN_SBDT
from PublicOpinion.stcn.sbgc import STCN_SBGC
from PublicOpinion.stcn.sdbd import STCN_SDBD
from PublicOpinion.stcn.space import STCN_Column
from PublicOpinion.stcn.ssgsyqb import STCN_SSGSYQB
from PublicOpinion.stcn.xingu import STCN_XinGu
from PublicOpinion.stcn.xwpl import STCN_XWPL
from PublicOpinion.stcn.yanbao import STCN_YanBao
from PublicOpinion.stcn.yaowen import STCN_YaoWen
from PublicOpinion.stcn.yqjj import STCN_YQJJ
from PublicOpinion.stcn.yqsl import STCN_YQSL
from PublicOpinion.stcn.yqyj import STCN_YQYJ
from PublicOpinion.stcn.zhuli import STCN_ZhuLi
from PublicOpinion.stcn.zijinliuxiang import STCN_ZiJinLiuXiang
from PublicOpinion.stcn.zxdt import ZXDT_YQJJ


def _run():
    print("开始爬取证券时报网 ")

    # 版块
    bankuai = STCN_BanKuai()
    bankuai.start()

    # 创投
    ct = STCN_ChuangTou()
    ct.start()

    # 公司
    company = STCN_Company()
    company.start()

    # 大盘
    dapan = STCN_DaPan()
    dapan.start()

    # 独家数据
    dj = STCN_DJSJ()
    dj.start()

    # 机构
    f = STCN_Finance()
    f.start()

    # 公司动态
    gs = STCN_GSDT()
    gs.start()

    # 国内
    guonei = STCN_GuoNei()
    guonei.start()

    # 海外
    haiwai = STCN_HaiWai()
    haiwai._start()

    # 看点数据
    kandianshuju = STCN_KanDianShuJu()
    kandianshuju.start()

    # 科创板
    d = STCN_KCB()
    d.start()

    # 快讯
    kuaixun = STCN_Kuaixun()
    kuaixun.start()

    # 股市
    market = STCN_Market()
    market.start()

    # 人物
    rw = STCN_RenWu()
    rw._start()

    # 滚动
    roll = STCN_Roll()
    roll.start()

    # 时报动态
    sbdt = STCN_SBDT()
    sbdt.start()

    # 时报观察
    sbgc = STCN_SBGC()
    sbgc.start()

    # 深度报道
    sd = STCN_SDBD()
    sd.start()

    # 专栏
    column = STCN_Column()
    column.start()

    # 上市公司舆情榜
    stcn_ssgsyqb = STCN_SSGSYQB()
    stcn_ssgsyqb._start()

    # 新股
    xingu = STCN_XinGu()
    xingu.start()

    # 评论
    pl = STCN_XWPL()
    pl.start()

    # 研报
    yanbao = STCN_YanBao()
    yanbao._start()

    # 要闻
    yaowen = STCN_YaoWen()
    yaowen._start()

    # 舆情聚焦
    yqjj = STCN_YQJJ()
    yqjj.start()

    #  舆情速览
    yqsl = STCN_YQSL()
    yqsl.start()

    # 舆情研究
    yqyj = STCN_YQYJ()
    yqyj.start()

    # 主力
    zhuli = STCN_ZhuLi()
    zhuli.start()

    # 资金流向
    zj = STCN_ZiJinLiuXiang()
    zj.start()

    # 中心动态
    zx = ZXDT_YQJJ()
    zx.start()


def run():
    try:
        _run()
    except:
        traceback.print_exc()


# 一共有 30 个实例 开启多线程进行爬取
def ins_start(instance):
    # 初始化的时间会去连接数据库
    # 将初始化放在这里执行

    # 或者在实例中 start 的时候再去 init pool
    instance.start()


def thread_run():
    bankuai = STCN_BanKuai()
    ct = STCN_ChuangTou()
    company = STCN_Company()
    dapan = STCN_DaPan()
    dj = STCN_DJSJ()
    f = STCN_Finance()
    gs = STCN_GSDT()
    guonei = STCN_GuoNei()
    haiwai = STCN_HaiWai()
    kandianshuju = STCN_KanDianShuJu()
    d = STCN_KCB()
    kuaixun = STCN_Kuaixun()
    market = STCN_Market()
    rw = STCN_RenWu()
    roll = STCN_Roll()
    sbdt = STCN_SBDT()
    sbgc = STCN_SBGC()
    sd = STCN_SDBD()
    column = STCN_Column()
    stcn_ssgsyqb = STCN_SSGSYQB()
    xingu = STCN_XinGu()
    pl = STCN_XWPL()
    yanbao = STCN_YanBao()
    yaowen = STCN_YaoWen()
    yqjj = STCN_YQJJ()
    yqsl = STCN_YQSL()
    yqyj = STCN_YQYJ()
    zhuli = STCN_ZhuLi()
    zj = STCN_ZiJinLiuXiang()
    zx = ZXDT_YQJJ()

    ins_list = [
        bankuai, ct, company, dapan, dj, f,
        gs, guonei, haiwai, kandianshuju, d, kuaixun,
        market, rw, roll, sbdt, sbgc, sd,
        column, stcn_ssgsyqb, xingu, pl, yanbao, yaowen,
        yqjj, yqsl, yqyj, zhuli, zj, zx,
    ]
    pool = threadpool.ThreadPool(4)
    reqs = threadpool.makeRequests(ins_start, ins_list)
    [pool.putRequest(req) for req in reqs]
    pool.wait()


# 直接运行
# run()

# 线程池运行
thread_run()
