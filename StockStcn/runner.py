import traceback

import threadpool

import sys
sys.path.append("./../../")

from StockStcn import STCN_BanKuai
from StockStcn import STCN_ChuangTou
from StockStcn import STCN_Company
from StockStcn.dapan import STCN_DaPan
from StockStcn.djsj import STCN_DJSJ
from StockStcn.finance import STCN_Finance
from StockStcn import STCN_GSDT
from StockStcn import STCN_GuoNei
from StockStcn import STCN_HaiWai
from StockStcn.kandianshuju import STCN_KanDianShuJu
from StockStcn.kcb import STCN_KCB
from StockStcn import STCN_Kuaixun
from StockStcn import STCN_Market
from StockStcn import STCN_RenWu
from StockStcn import STCN_Roll
from StockStcn.sbdt import STCN_SBDT
from StockStcn.sbgc import STCN_SBGC
from StockStcn import STCN_SDBD
from StockStcn.space import STCN_Column
from StockStcn import STCN_SSGSYQB
from StockStcn import STCN_XinGu
from StockStcn.xwpl import STCN_XWPL
from StockStcn.yanbao import STCN_YanBao
from StockStcn import STCN_YaoWen
from StockStcn import STCN_YQJJ
from StockStcn import STCN_YQSL
from StockStcn import STCN_YQYJ
from StockStcn.zhuli import STCN_ZhuLi
from StockStcn.zijinliuxiang import STCN_ZiJinLiuXiang
from StockStcn import ZXDT_YQJJ


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

    # 舆情速览
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
run()

# 线程池运行
# thread_run()
