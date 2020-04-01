## 小型爬虫 基于 docker + apscheduler 部署

## 舆情 PublicOpinion
- 东财财富号 [表名: eastmoney_carticle] 
    - 模块: PublicOpinion/carticle

- 淘股吧 [taoguba]
    - PublicOpinion/taoguba 

- 网易财经 [netease_money]
    - PublicOpinion/netease_money.py 

- 腾讯 A 股网页版 [qq_astock_news]
    - PublicOpinion/qq_stock.py 

- 上海证券报 [cn_stock]
    - 要闻-宏观 qmt-sns_yw
    - 要闻-金融 qmt-sns_jg 
    - 公司-公司聚焦 qmt-scp_gsxw 
    - 公司-公告快讯 qmt-tjd_ggkx 
    - 公司-公告解读 qmt-tjd_bbdj 
    - 市场-直播 qmt-smk_gszbs 
    - 市场-新股-新股聚焦 qmt-sx_xgjj 
    - 市场-新股-政策动态 qmt-sx_zcdt 
    - 市场-新股-新股策略 qmt-sx_xgcl 
    - 市场-新股-IPO评论 qmt-sx_ipopl 
    - 市场-基金 qmt-smk_jjdx 
    - 市场-券业 qmt-sns_qy 
    - 市场-债券 qmt-smk_zq 
    - 市场-信托 qmt-smk_xt 
    - 科创板-要闻 qmt-skc_tt 
    - 科创板-监管 qmt-skc_jgfx 
    - 科创板-公司 qmt-skc_sbgsdt 
    - 科创板-投资 qmt-skc_tzzn 
    - 科创板-观点 qmt-skc_gd 
    - 新三板-要闻 qmt-sjrz_yw 
    - 上证四小时  PublicOpinion/cn_4_hours.py 

- 巨潮资讯 [juchao_info]
    - PublicOpinion/juchao.py 

- 证券时报 [stcn_info]  
    - 版块 PublicOpinion/stcn/bankuai.py 
    - 创投 PublicOpinion/stcn/chuangtou.py 
    - 公司 PublicOpinion/stcn/company.py 
    - 大盘 PublicOpinion/stcn/dapan.py 
    - 独家数据 PublicOpinion/stcn/djsj.py 
    - 机构 PublicOpinion/stcn/finance.py 
    - 公司动态 PublicOpinion/stcn/gsdt.py 
    - 国内 PublicOpinion/stcn/guonei.py 
    - 海外 PublicOpinion/stcn/haiwai.py 
    - 看点数据 PublicOpinion/stcn/kandianshuju.py 
    - 科创板 PublicOpinion/stcn/kcb.py 
    - 快讯 PublicOpinion/stcn/kuaixun.py 
    - 股市 PublicOpinion/stcn/market.py
    - 人物 PublicOpinion/stcn/renwu.py 
    - 滚动 PublicOpinion/stcn/renwu.py 
    - 时报动态 PublicOpinion/stcn/sbdt.py 
    - 时报观察 PublicOpinion/stcn/sbgc.py 
    - 深度报道 PublicOpinion/stcn/sdbd.py 
    - 专栏 PublicOpinion/stcn/space.py 
    - 上市公司舆情榜 PublicOpinion/stcn/ssgsyqb.py 
    - 新股 PublicOpinion/stcn/xingu.py 
    - 评论 PublicOpinion/stcn/xwpl.py 
    - 研报 PublicOpinion/stcn/yanbao.py 
    - 要闻 PublicOpinion/stcn/yaowen.py 
    - 舆情聚焦 PublicOpinion/stcn/yqjj.py 
    - 舆情速览 PublicOpinion/stcn/yqsl.py 
    - 舆情研究 PublicOpinion/stcn/yqyj.py 
    - 主力 PublicOpinion/stcn/zhuli.py 
    - 资金流向 PublicOpinion/stcn/zijinliuxiang.py 
    - 中心动态 PublicOpinion/stcn/zxdt.py 
 
- 财新社[cls_afteraffichelist, cls_depth_theme, cls_telegraphs]
    - 电报 PublicOpinion/cls_cn/telegraphs.py 
    - 深度、题材等 PublicOpinion/cls_cn/depth.py 
    - 内参 PublicOpinion/cls_cn/reference.py
        - 早报 morningNewsList
        - 每日收评 everydayReceiveList 
        - 新闻联播 networkNewsList 
        - 证监发布会 csrcList 
        - 环球市场 globaMarketList 
        - 涨停预测 forecastList 
        - 热点版块 hotPlateList 
        - 明日 3 大猜想 threeGuessList 

- 大公报财经[takungpao]
    - 港股频道 
        - 财经时事 PublicOpinion/takungpao/hkstock_cjss.py
        - 公司要闻 PublicOpinion/takungpao/hkstock_gsyw.py
        - 机构视点 PublicOpinion/takungpao/hkstock_jgsd.py
        - 全球股市 PublicOpinion/takungpao/hkstock_qqgs.py
        - 国际聚焦 PublicOpinion/takungpao/hkstock_gjjj.py 
        - 经济一周 PublicOpinion/takungpao/hkstock_jjyz.py 
    - 风口: PublicOpinion/takungpao/takungpao_fk.py 
    - 旅游: PublicOpinion/takungpao/takungpao_travel.py 
    - 首页财经 
        - 中国经济  PublicOpinion/takungpao/zhongguojingji.py 
        - 香港财经  PublicOpinion/takungpao/hkcaijing.py 
        - 国际经济  PublicOpinion/takungpao/guojijingji.py 
        - 经济观察家  PublicOpinion/takungpao/economic_observer.py 
        - 港股  PublicOpinion/takungpao/hk_stock.py 
        - 地产  PublicOpinion/takungpao/dichan.py 
        - 商业  PublicOpinion/takungpao/business.py 
        - 新经济浪潮  PublicOpinion/takungpao/economic_observer.py 
    

## 官媒 GovSpiders
- 中国银行 [chinabank]
    - 数据解读
    - 新闻发布

- 国家统计局 [gov_stats]
    - 数据解读 
    - 统计动态
    - 新闻发布会
    - 最新发布

## 陆股通 
- 实时数据 
    - 网址： http://data.eastmoney.com/hsgt/index.html 
    - 爬虫表： lgt_south_money_data; lgt_north_money_data 
    - 数据中心表: hkland_flow 
- 陆港通-每日持股明细
    - 网址： https://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh&t=sh 
    - 爬虫表： hold_shares_sz, hold_shares_sh, hold_shares_hk 
    - 数据中心表: hkland_shares hkland_hkshares 
- 陆港通历史数据 
    - 网址: http://data.eastmoney.com/hsgt/index.html 
    - 爬虫表： lgt_historical_data 
    - 数据中心表： hkland_historytradestat 
- 陆港通十大成交股  
    - 网址： http://data.eastmoney.com/hsgt/index.html 
    - 爬虫表: lgt_ten_traded_shares 
    - 数据中心表: hkland_toptrade 
- 交易日历 
    - 上交所： 
        - 网址： http://www.sse.com.cn/services/hkexsc/home/ 
        - 爬虫表： trading_calendar_sh
        - 数据中心表： calendar_hkland_shsz 
    - 深交所： 
        - 网址： http://www.szse.cn/szhk/index.html 
        - 爬虫表： trading_calendar_sz 
        - 数据中心表： calendar_hkland_shsz 
    - 港交所： 
        - 网址： https://sc.hkex.com.hk/TuniS/www.hkex.com.hk/News/HKEX-Calendar 
        - 爬虫表： trading_calendar_hk 
        - 数据中心表： calendar_hkland_hk 
- 陆股通持股统计 
    - 网址：  https://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh&t=sh 
    - 爬虫表： hold_shares_sh  hold_shares_sz 
    - 数据中心表： hkland_hkscc 
