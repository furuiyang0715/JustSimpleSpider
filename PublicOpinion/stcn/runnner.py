import traceback

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
    d = STCN_Company()
    d.start()

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
    kuaixun = STCN_Roll()
    kuaixun.start()

    # 时报动态
    sb = STCN_SBDT()
    sb.start()

    # 时报观察
    sb = STCN_SBGC()
    sb.start()

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


run()
