import datetime
import pprint
import sys

import requests as re
from lxml import html


def parse_next():

    pass


def parse_list(body):
    items = []
    doc = html.fromstring(body)
    news_list = doc.xpath("//div[@class='m_txt_news']/ul/li")
    # print(news_list)
    # print(len(news_list))
    for news in news_list:
        item = {}
        title = news.xpath("./a[@class='a_title']")
        if not title:
            title = news.xpath("./a[@class='a_title txt_blod']")
        title = title[0].text_content()
        # print(title)
        item['title'] = title
        pub_date = news.xpath("./a[@class='a_time txt_blod']")
        if not pub_date:
            pub_date = news.xpath("./a[@class='a_time']")

        link = pub_date[0].xpath("./@href")[0]
        # print(link)
        item['link'] = link

        pub_date = pub_date[0].text_content()
        # print(pub_date)
        item['pub_date'] = pub_date
        items.append(item)
    return items


# url = 'http://finance.takungpao.com/hkstock/cjss/'
# url = 'http://finance.takungpao.com/hkstock/cjss/index_4.html'
# body = re.get(url).text
# items = parse_list(body)
# print(pprint.pformat(items))
# print(len(items))

# zhongguojingji = 'http://www.takungpao.com/finance/236132/index.html'
zhongguojingji = 'http://www.takungpao.com/finance/236132/2.html'
# Economic_observer 经济观察家
ob = "http://www.takungpao.com/finance/236134/index.html"
body = re.get(ob).text
# print(body)
doc = html.fromstring(body)
news_list = doc.xpath('//div[@class="sublist_mobile"]/dl[@class="item"]')
print(len(news_list))

# sys.exit(0)

for news in news_list:
    link = news.xpath('./dd[@class="intro"]/a/@href')[0]
    print(link)

    title = news.xpath("./dd/a/@title")
    print(title[0])

    pub_date = news.xpath("./dd[@class='date']/text()")[0]
    # # 发布时间的几种处理
    print(">>> ", pub_date)
    current_dt = datetime.datetime.now()
    yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    after_yesterday_dt_str = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    if "小时前" in pub_date:  # eg. 20小时前
        hours = int(pub_date.replace('小时前', ''))
        pub_date = (current_dt - datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    elif "昨天" in pub_date:  # eg. 昨天04:24
        pub_date = pub_date.replace('昨天', '')
        pub_date = " ".join([yesterday_dt_str, pub_date])
    elif '前天' in pub_date:   # eg. 前天11:33
        pub_date = pub_date.replace("前天", '')
        pub_date = " ".join([after_yesterday_dt_str, pub_date])
    else:    # eg. 02-29 04:24
        pub_date = str(current_dt.year) + '-' + pub_date
    print(pub_date)
    print()



'''
<div class="sublist_mobile">
        <dl class="item">
            <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0303/422018.html" target="_blank" title="﻿楼语纵横\全民派钱助经济复甦">
            <img src="http://img.takungpao.com/2020/0303/20200303042402358.jpg" alt="﻿楼语纵横\全民派钱助经济复甦"></a></dt>            
            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0303/422018.html" title="﻿楼语纵横\全民派钱助经济复甦" target="_blank">﻿楼语纵横\全民派钱助经济复甦</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0303/422018.html" target="_blank"></a></dd>
            <dd class="date">6小时前<a href="http://www.takungpao.com/finance/236134/2020/0303/422018.html" target="_blank" class="more"></a></dd>
        </dl>
        
        <dl class="item">
            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0303/422016.html" title="﻿财眼看房\期待内地稳定楼市措施" target="_blank">﻿财眼看房\期待内地稳定楼市措施</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0303/422016.html" target="_blank"></a></dd>
            <dd class="date">6小时前<a href="http://www.takungpao.com/finance/236134/2020/0303/422016.html" target="_blank" class="more"></a></dd>
        </dl>
        
        <dl class="item">
            <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0303/422014.html" target="_blank" title="钟言谠论\美股走势左右大选"><img src="http://img.takungpao.com/2020/0303/20200303081435735.jpg" alt="钟言谠论\美股走势左右大选"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0303/422014.html" title="钟言谠论\美股走势左右大选" target="_blank">钟言谠论\美股走势左右大选</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0303/422014.html" target="_blank">如果疫情继续发展，美股继续下跌，那么特朗普连任概率必然出现下降，甚至其在医疗救助上的不利很可能被民主党所针对性攻击。</a></dd>
            <dd class="date">6小时前<a href="http://www.takungpao.com/finance/236134/2020/0303/422014.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0302/421635.html" title="﻿楼按明鉴\现时係转按好时机？（一）" target="_blank">﻿楼按明鉴\现时係转按好时机？（一）</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0302/421635.html" target="_blank"></a></dd>
            <dd class="date">昨天04:24<a href="http://www.takungpao.com/finance/236134/2020/0302/421635.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0302/421633.html" target="_blank" title="﻿链能讲堂\区块链新规利产业发展"><img src="http://img.takungpao.com/2020/0302/20200302042403329.jpg" alt="﻿链能讲堂\区块链新规利产业发展"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0302/421633.html" title="﻿链能讲堂\区块链新规利产业发展" target="_blank">﻿链能讲堂\区块链新规利产业发展</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0302/421633.html" target="_blank"></a></dd>
            <dd class="date">昨天04:24<a href="http://www.takungpao.com/finance/236134/2020/0302/421633.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0302/421631.html" target="_blank" title="﻿至诚颖评\大湾区发展日新月异"><img src="http://img.takungpao.com/2020/0302/20200302080455789.jpg" alt="﻿至诚颖评\大湾区发展日新月异"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0302/421631.html" title="﻿至诚颖评\大湾区发展日新月异" target="_blank">﻿至诚颖评\大湾区发展日新月异</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0302/421631.html" target="_blank">湾区发展身处什么阶段？湾区政策的用意和力度如何？有意入局的港人应何去何从？笔者将检视过去一年的湾区发展规划和实践状况，以资参考。</a></dd>
            <dd class="date">昨天04:24<a href="http://www.takungpao.com/finance/236134/2020/0302/421631.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0229/421090.html" title="﻿主楼布阵\楼价最终还看供需格局\美联物业住宅部行政总裁 布少明" target="_blank">﻿主楼布阵\楼价最终还看供需格局\美联物业住宅部行政总裁 布少明</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0229/421090.html" target="_blank"></a></dd>
            <dd class="date">02-29 04:23<a href="http://www.takungpao.com/finance/236134/2020/0229/421090.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0229/421088.html" target="_blank" title="﻿斌眼观市\外围波动对A股影响有限\西南证券首席策略分析师 朱 斌"><img src="http://img.takungpao.com/2020/0229/20200229042357404.jpg" alt="﻿斌眼观市\外围波动对A股影响有限\西南证券首席策略分析师 朱 斌"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0229/421088.html" title="﻿斌眼观市\外围波动对A股影响有限\西南证券首席策略分析师 朱 斌" target="_blank">﻿斌眼观市\外围波动对A股影响有限\西南证券首席策略分析师 朱 斌</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0229/421088.html" target="_blank"></a></dd>
            <dd class="date">02-29 04:23<a href="http://www.takungpao.com/finance/236134/2020/0229/421088.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0229/421086.html" target="_blank" title="﻿领军智库\黄金为何与美股同跌\中国外汇投资研究院分析师 彭天舒 宋云"><img src="http://img.takungpao.com/2020/0229/20200229042356930.jpg" alt="﻿领军智库\黄金为何与美股同跌\中国外汇投资研究院分析师 彭天舒 宋云"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0229/421086.html" title="﻿领军智库\黄金为何与美股同跌\中国外汇投资研究院分析师 彭天舒 宋云" target="_blank">﻿领军智库\黄金为何与美股同跌\中国外汇投资研究院分析师 彭天舒 宋云</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0229/421086.html" target="_blank"></a></dd>
            <dd class="date">02-29 04:23<a href="http://www.takungpao.com/finance/236134/2020/0229/421086.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0228/420697.html" title="﻿楼市智库\政商各界齐出手稳楼市\中原亚太区副主席兼住宅部总裁 陈永杰" target="_blank">﻿楼市智库\政商各界齐出手稳楼市\中原亚太区副主席兼住宅部总裁 陈永杰</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0228/420697.html" target="_blank"></a></dd>
            <dd class="date">02-28 04:23<a href="http://www.takungpao.com/finance/236134/2020/0228/420697.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0228/420695.html" title="﻿实话世经\结构性政策助力经济战疫\工银国际首席经济学家、董事总经理 程 实" target="_blank">﻿实话世经\结构性政策助力经济战疫\工银国际首席经济学家、董事总经理 程 实</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0228/420695.html" target="_blank">　　会当凌绝顶，一览众山小。复工相比去年同期进度缓慢，虽然增加了现实的经济压力，但也在客观上起到了时间换空间的战略作用。疫情演进、   </a></dd>
            <dd class="date">02-28 04:23<a href="http://www.takungpao.com/finance/236134/2020/0228/420695.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0228/420693.html" target="_blank" title="﻿至诚颖评\三建议促进防疫复工"><img src="http://img.takungpao.com/2020/0228/20200228080438891.jpg" alt="﻿至诚颖评\三建议促进防疫复工"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0228/420693.html" title="﻿至诚颖评\三建议促进防疫复工" target="_blank">﻿至诚颖评\三建议促进防疫复工</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0228/420693.html" target="_blank">新冠肺炎疫情爆发至今，各地政府为了控制疫情，新春后复工进展还不太理想。中央政府接连展开会议，提出有序复工复产。</a></dd>
            <dd class="date">02-28 04:23<a href="http://www.takungpao.com/finance/236134/2020/0228/420693.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0227/420347.html" title="﻿楼市强心针\疫症重临 楼市今非昔比\利嘉阁地产总裁 廖伟强" target="_blank">﻿楼市强心针\疫症重临 楼市今非昔比\利嘉阁地产总裁 廖伟强</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0227/420347.html" target="_blank"></a></dd>
            <dd class="date">02-27 04:24<a href="http://www.takungpao.com/finance/236134/2020/0227/420347.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0227/420345.html" title="﻿教孩子看财案：三原则 四方向\校长爸爸教理财 关显彬" target="_blank">﻿教孩子看财案：三原则 四方向\校长爸爸教理财 关显彬</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0227/420345.html" target="_blank"></a></dd>
            <dd class="date">02-27 04:24<a href="http://www.takungpao.com/finance/236134/2020/0227/420345.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0227/420343.html" target="_blank" title="财经石评\统筹兼顾防疫与复工\同济大学财经研究所所长教授 石建勋"><img src="http://img.takungpao.com/2020/0227/20200227081528263.jpg" alt="财经石评\统筹兼顾防疫与复工\同济大学财经研究所所长教授 石建勋"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0227/420343.html" title="财经石评\统筹兼顾防疫与复工\同济大学财经研究所所长教授 石建勋" target="_blank">财经石评\统筹兼顾防疫与复工\同济大学财经研究所所长教授 石建勋</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0227/420343.html" target="_blank">复工复产既是经济社会正常运行和发展的必须，也是打赢疫情防控总体战和阻击战之必须，要精准施策，以过硬的手段抓实抓好复工复产。</a></dd>
            <dd class="date">02-27 04:24<a href="http://www.takungpao.com/finance/236134/2020/0227/420343.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0226/419931.html" target="_blank" title="﻿楼市新态\龙市下的巩固底线\祥益地产总裁 汪敦敬"><img src="http://img.takungpao.com/2020/0226/20200226042402208.jpg" alt="﻿楼市新态\龙市下的巩固底线\祥益地产总裁 汪敦敬"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0226/419931.html" title="﻿楼市新态\龙市下的巩固底线\祥益地产总裁 汪敦敬" target="_blank">﻿楼市新态\龙市下的巩固底线\祥益地产总裁 汪敦敬</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0226/419931.html" target="_blank"></a></dd>
            <dd class="date">02-26 04:24<a href="http://www.takungpao.com/finance/236134/2020/0226/419931.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0226/419929.html" title="﻿超限观点\明晰复工复产路线图\海通证券首席宏观分析师 姜 超" target="_blank">﻿超限观点\明晰复工复产路线图\海通证券首席宏观分析师 姜 超</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0226/419929.html" target="_blank"></a></dd>
            <dd class="date">02-26 04:24<a href="http://www.takungpao.com/finance/236134/2020/0226/419929.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0226/419927.html" target="_blank" title="﻿明观四海\湾区发展的两个新方向\丝路智谷研究院院长 梁海明"><img src="http://img.takungpao.com/2020/0226/20200226080336139.jpg" alt="﻿明观四海\湾区发展的两个新方向\丝路智谷研究院院长 梁海明"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0226/419927.html" title="﻿明观四海\湾区发展的两个新方向\丝路智谷研究院院长 梁海明" target="_blank">﻿明观四海\湾区发展的两个新方向\丝路智谷研究院院长 梁海明</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0226/419927.html" target="_blank">那么，粤港澳大湾区近期该朝什么方向着力，才能一方面更紧贴规划的要求，另一方面更有利于为中国的城市群，乃至为世界经济未来的发展树立规范呢？</a></dd>
            <dd class="date">02-26 04:24<a href="http://www.takungpao.com/finance/236134/2020/0226/419927.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0225/419555.html" title="﻿楼语纵横\楼市调整非熊市开始" target="_blank">﻿楼语纵横\楼市调整非熊市开始</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0225/419555.html" target="_blank"></a></dd>
            <dd class="date">02-25 04:24<a href="http://www.takungpao.com/finance/236134/2020/0225/419555.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0225/419553.html" title="﻿隔岸观市\对经济形势要客观评估" target="_blank">﻿隔岸观市\对经济形势要客观评估</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0225/419553.html" target="_blank"></a></dd>
            <dd class="date">02-25 04:24<a href="http://www.takungpao.com/finance/236134/2020/0225/419553.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0225/419551.html" target="_blank" title="﻿交银观察\疫情结束前勿盲目乐观"><img src="http://img.takungpao.com/2020/0225/20200225081242910.jpg" alt="﻿交银观察\疫情结束前勿盲目乐观"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0225/419551.html" title="﻿交银观察\疫情结束前勿盲目乐观" target="_blank">﻿交银观察\疫情结束前勿盲目乐观</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0225/419551.html" target="_blank">伴随诸多好消息的出现，人们对疫情的“心理拐点”已然到来。但从实际情况看，多方面迹象表明，疫情真正的拐点尚未出现。当前，部分地区出现“报复式”刺激经济增长的苗头，需要予以警惕和及时纠正。</a></dd>
            <dd class="date">02-25 04:24<a href="http://www.takungpao.com/finance/236134/2020/0225/419551.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0224/419165.html" target="_blank" title="﻿谈楼说按\白居二按揭探究（上）\中原按揭经纪董事总经理 王美凤"><img src="http://img.takungpao.com/2020/0224/20200224042359102.jpg" alt="﻿谈楼说按\白居二按揭探究（上）\中原按揭经纪董事总经理 王美凤"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0224/419165.html" title="﻿谈楼说按\白居二按揭探究（上）\中原按揭经纪董事总经理 王美凤" target="_blank">﻿谈楼说按\白居二按揭探究（上）\中原按揭经纪董事总经理 王美凤</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0224/419165.html" target="_blank"></a></dd>
            <dd class="date">02-24 04:23<a href="http://www.takungpao.com/finance/236134/2020/0224/419165.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0224/419163.html" target="_blank" title="﻿大湾区各城市2018年GDP一览（单位：美元）"><img src="http://img.takungpao.com/2020/0224/20200224042358692.jpg" alt="﻿大湾区各城市2018年GDP一览（单位：美元）"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0224/419163.html" title="﻿大湾区各城市2018年GDP一览（单位：美元）" target="_blank">﻿大湾区各城市2018年GDP一览（单位：美元）</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0224/419163.html" target="_blank"></a></dd>
            <dd class="date">02-24 04:23<a href="http://www.takungpao.com/finance/236134/2020/0224/419163.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0224/419161.html" target="_blank" title="香江畔的思索\大湾区金融联通稳步扩展"><img src="http://img.takungpao.com/2020/0224/20200224080318138.jpg" alt="香江畔的思索\大湾区金融联通稳步扩展"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0224/419161.html" title="香江畔的思索\大湾区金融联通稳步扩展" target="_blank">香江畔的思索\大湾区金融联通稳步扩展</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0224/419161.html" target="_blank">目前国家整体金融市场的开放已取得相当进展，而港澳一直扮演国家金融开放的门户的角色，诸多推动国内国际金融市场互联互通的机制都是从港澳开始落实的。</a></dd>
            <dd class="date">02-24 04:23<a href="http://www.takungpao.com/finance/236134/2020/0224/419161.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0222/418617.html" target="_blank" title="﻿主楼布阵\笋租盘“疫市”湧现\美联物业住宅部行政总裁 布少明"><img src="http://img.takungpao.com/2020/0222/20200222042406312.jpg" alt="﻿主楼布阵\笋租盘“疫市”湧现\美联物业住宅部行政总裁 布少明"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0222/418617.html" title="﻿主楼布阵\笋租盘“疫市”湧现\美联物业住宅部行政总裁 布少明" target="_blank">﻿主楼布阵\笋租盘“疫市”湧现\美联物业住宅部行政总裁 布少明</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0222/418617.html" target="_blank"></a></dd>
            <dd class="date">02-22 04:24<a href="http://www.takungpao.com/finance/236134/2020/0222/418617.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0222/418615.html" target="_blank" title="﻿深度涛解\疫情下的中国财政扩张空间\天风证券首席宏观分析师 宋雪涛"><img src="http://img.takungpao.com/2020/0222/20200222042405937.jpg" alt="﻿深度涛解\疫情下的中国财政扩张空间\天风证券首席宏观分析师 宋雪涛"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0222/418615.html" title="﻿深度涛解\疫情下的中国财政扩张空间\天风证券首席宏观分析师 宋雪涛" target="_blank">﻿深度涛解\疫情下的中国财政扩张空间\天风证券首席宏观分析师 宋雪涛</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0222/418615.html" target="_blank"></a></dd>
            <dd class="date">02-22 04:24<a href="http://www.takungpao.com/finance/236134/2020/0222/418615.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0221/418222.html" target="_blank" title="﻿楼市智库\疫情下物业投资更稳健\中原亚太区副主席兼住宅部总裁 陈永杰"><img src="http://img.takungpao.com/2020/0221/20200221042358675.jpg" alt="﻿楼市智库\疫情下物业投资更稳健\中原亚太区副主席兼住宅部总裁 陈永杰"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0221/418222.html" title="﻿楼市智库\疫情下物业投资更稳健\中原亚太区副主席兼住宅部总裁 陈永杰" target="_blank">﻿楼市智库\疫情下物业投资更稳健\中原亚太区副主席兼住宅部总裁 陈永杰</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0221/418222.html" target="_blank"></a></dd>
            <dd class="date">02-21 04:23<a href="http://www.takungpao.com/finance/236134/2020/0221/418222.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0221/418220.html" title="﻿链能讲堂\数字资产的确权价值\香港国际新经济研究院 高级研究员 付 饶" target="_blank">﻿链能讲堂\数字资产的确权价值\香港国际新经济研究院 高级研究员 付 饶</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0221/418220.html" target="_blank"></a></dd>
            <dd class="date">02-21 04:23<a href="http://www.takungpao.com/finance/236134/2020/0221/418220.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0221/418218.html" target="_blank" title="钟言谠论\港股下季行情值得期待"><img src="http://img.takungpao.com/2020/0221/20200221082248455.jpg" alt="钟言谠论\港股下季行情值得期待"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0221/418218.html" title="钟言谠论\港股下季行情值得期待" target="_blank">钟言谠论\港股下季行情值得期待</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0221/418218.html" target="_blank">笔者预计，恒生指数一季度EPS环比增速大致在-10%到-5%之间，二季度EPS的环比大致在+6%到+11%之间，也就是二季度将完全填补上一季度的损失。</a></dd>
            <dd class="date">02-21 04:23<a href="http://www.takungpao.com/finance/236134/2020/0221/418218.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0220/417742.html" title="﻿楼市强心针\疫情过后港楼价或反弹" target="_blank">﻿楼市强心针\疫情过后港楼价或反弹</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0220/417742.html" target="_blank"></a></dd>
            <dd class="date">02-20 04:23<a href="http://www.takungpao.com/finance/236134/2020/0220/417742.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0220/417740.html" title="﻿建言献策\停工累内地民企利润锐减" target="_blank">﻿建言献策\停工累内地民企利润锐减</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0220/417740.html" target="_blank"></a></dd>
            <dd class="date">02-20 04:23<a href="http://www.takungpao.com/finance/236134/2020/0220/417740.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0220/417738.html" title="﻿见微知市\内地社保减费支援企业" target="_blank">﻿见微知市\内地社保减费支援企业</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0220/417738.html" target="_blank">全国所有中小微企业及湖北各类企业阶段性“豁免期”为2020年2月至6月，共有五个月；湖北以外各省的大型企业减半缴费“优惠期”为2020年2月至4月，共有三个月。</a></dd>
            <dd class="date">02-20 04:23<a href="http://www.takungpao.com/finance/236134/2020/0220/417738.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0219/417410.html" title="﻿楼市新态\淡市减辣合情合理\祥益地产总裁 汪敦敬" target="_blank">﻿楼市新态\淡市减辣合情合理\祥益地产总裁 汪敦敬</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0219/417410.html" target="_blank"></a></dd>
            <dd class="date">02-19 04:24<a href="http://www.takungpao.com/finance/236134/2020/0219/417410.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0219/417408.html" title="﻿领军智库\疫情之后如何稳外贸\中国外汇投资研究院特约分析师 古 宇" target="_blank">﻿领军智库\疫情之后如何稳外贸\中国外汇投资研究院特约分析师 古 宇</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0219/417408.html" target="_blank"></a></dd>
            <dd class="date">02-19 04:24<a href="http://www.takungpao.com/finance/236134/2020/0219/417408.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0219/417406.html" target="_blank" title="察股观经\节后复工不足六成\中泰证券首席经济学家 李迅雷"><img src="http://img.takungpao.com/2020/0219/20200219083811383.jpg" alt="察股观经\节后复工不足六成\中泰证券首席经济学家 李迅雷"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0219/417406.html" title="察股观经\节后复工不足六成\中泰证券首席经济学家 李迅雷" target="_blank">察股观经\节后复工不足六成\中泰证券首席经济学家 李迅雷</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0219/417406.html" target="_blank">近期主要工业行业的去库存压力在明显增大，积极的政策会更快的推出。</a></dd>
            <dd class="date">02-19 04:24<a href="http://www.takungpao.com/finance/236134/2020/0219/417406.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0218/417037.html" title="﻿楼语纵横\还息不还本 助业主抗疫\Q房网香港董事总经理 陈坤兴" target="_blank">﻿楼语纵横\还息不还本 助业主抗疫\Q房网香港董事总经理 陈坤兴</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0218/417037.html" target="_blank"></a></dd>
            <dd class="date">02-18 04:23<a href="http://www.takungpao.com/finance/236134/2020/0218/417037.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0218/417035.html" title="﻿青创时代\站在新起点推进大湾区建设\香港青年创新创业协会理事 赵 阳" target="_blank">﻿青创时代\站在新起点推进大湾区建设\香港青年创新创业协会理事 赵 阳</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0218/417035.html" target="_blank"></a></dd>
            <dd class="date">02-18 04:23<a href="http://www.takungpao.com/finance/236134/2020/0218/417035.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                <dt class="pic"><a href="http://www.takungpao.com/finance/236134/2020/0218/417033.html" target="_blank" title="创科宇宙\卫生防疫产业孕育而生\创业投资者联盟召集人 梁颕宇"><img src="http://img.takungpao.com/2020/0218/20200218082351309.jpg" alt="创科宇宙\卫生防疫产业孕育而生\创业投资者联盟召集人 梁颕宇"></a></dt>            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0218/417033.html" title="创科宇宙\卫生防疫产业孕育而生\创业投资者联盟召集人 梁颕宇" target="_blank">创科宇宙\卫生防疫产业孕育而生\创业投资者联盟召集人 梁颕宇</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0218/417033.html" target="_blank">今天内地的医疗科技和研发能力已大大提升，几乎可以肯定地说，待到打胜这场疫战后，必定能再上一个新的台阶。</a></dd>
            <dd class="date">02-18 04:23<a href="http://www.takungpao.com/finance/236134/2020/0218/417033.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0217/416620.html" title="﻿楼按明鉴\银行支援措施助人助己\经络按揭转介高级副总裁 曹德明" target="_blank">﻿楼按明鉴\银行支援措施助人助己\经络按揭转介高级副总裁 曹德明</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0217/416620.html" target="_blank"></a></dd>
            <dd class="date">02-17 04:23<a href="http://www.takungpao.com/finance/236134/2020/0217/416620.html" target="_blank" class="more"></a></dd>
        </dl>
                                <dl class="item">
                            <dd class="title"><a href="http://www.takungpao.com/finance/236134/2020/0217/416618.html" title="﻿外汇观察\长期增长抵销短期风险\中国外汇投资研究院金融分析师 宋云明" target="_blank">﻿外汇观察\长期增长抵销短期风险\中国外汇投资研究院金融分析师 宋云明</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236134/2020/0217/416618.html" target="_blank"></a></dd>
            <dd class="date">02-17 04:23<a href="http://www.takungpao.com/finance/236134/2020/0217/416618.html" target="_blank" class="more"></a></dd>
        </dl>
                                 </div>
'''



