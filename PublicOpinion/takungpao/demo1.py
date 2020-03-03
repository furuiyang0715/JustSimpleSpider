import datetime
import pprint

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
'''

<div class="wrap_left">
    
        <dl class="item clearfix">
                <dt><a href="http://www.takungpao.com/finance/236132/2020/0302/421804.html" target="_blank" title="2月份全国铁路发送货物同比增长4.5%"><img src="http://img.takungpao.com/2020/0302/20200302010218508.jpg" alt="2月份全国铁路发送货物同比增长4.5%"></a></dt>            <dd><a href="http://www.takungpao.com/finance/236132/2020/0302/421804.html" title="2月份全国铁路发送货物同比增长4.5%" target="_blank">2月份全国铁路发送货物同比增长4.5%</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0302/421804.html" target="_blank">2月份，全国铁路累计发送货物3 1亿吨，同比增长4 5%。自2月17日以来，日发送货物已连续13天在1100万吨以上。</a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">央视新闻客户端</em>4小时前</dd>
        </dl>
                                <dl class="item clearfix">
                <dt><a href="http://www.takungpao.com/finance/236132/2020/0302/421801.html" target="_blank" title="赛轮沈阳300万套高性能智能化全钢胎项目开工建设"><img src="http://img.takungpao.com/2020/0302/20200302123947817.jpg" alt="赛轮沈阳300万套高性能智能化全钢胎项目开工建设"></a></dt>            <dd><a href="http://www.takungpao.com/finance/236132/2020/0302/421801.html" title="赛轮沈阳300万套高性能智能化全钢胎项目开工建设" target="_blank">赛轮沈阳300万套高性能智能化全钢胎项目开工建设</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0302/421801.html" target="_blank">3月1日，赛轮沈阳年产300万套高性能智能化全钢载重子午线轮胎项目正式开工建设。据了解，该项目达产后，赛轮沈阳工厂将形成年产500万套全钢载重子午线轮胎的产能规模，成为全球最大的全钢子午线轮胎单体工厂之一。</a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">第一产经网</em>5小时前</dd>
        </dl>
                                <dl class="item clearfix">
                <dt><a href="http://www.takungpao.com/finance/236132/2020/0302/421781.html" target="_blank" title="甘肃“线上”发布3700亿重点招商引资项目"><img src="http://img.takungpao.com/2020/0302/20200302103108215.jpeg" alt="甘肃“线上”发布3700亿重点招商引资项目"></a></dt>            <dd><a href="http://www.takungpao.com/finance/236132/2020/0302/421781.html" title="甘肃“线上”发布3700亿重点招商引资项目" target="_blank">甘肃“线上”发布3700亿重点招商引资项目</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0302/421781.html" target="_blank">日前，为应对疫情防控期间对招商引资工作的不利影响，甘肃省商务厅、甘肃省经济合作局联合兰州市政府、临夏州政府及浙商杂志社举办了甘肃省招商引资项目线上推介会。</a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name"> 刘俊海</em>7小时前</dd>
        </dl>
                                <dl class="item clearfix">
                <dt><a href="http://www.takungpao.com/finance/236132/2020/0302/421772.html" target="_blank" title="我国口罩日产能产量双双突破1亿只"><img src="http://img.takungpao.com/2020/0211/20200211124259843.jpg" alt="我国口罩日产能产量双双突破1亿只"></a></dt>            <dd><a href="http://www.takungpao.com/finance/236132/2020/0302/421772.html" title="我国口罩日产能产量双双突破1亿只" target="_blank">我国口罩日产能产量双双突破1亿只</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0302/421772.html" target="_blank">记者今天（2日）从国家发展改革委了解到，我国口罩日产能产量连续快速增长，双双突破1亿只。</a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">央视新闻客户端 戈晓威</em>8小时前</dd>
        </dl>
                                <dl class="item clearfix">
                            <dd><a href="http://www.takungpao.com/finance/236132/2020/0302/421699.html" title="﻿应对挑战\配套措施有待加强" target="_blank">﻿应对挑战\配套措施有待加强</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0302/421699.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>13小时前</dd>
        </dl>
                                <dl class="item clearfix">
                            <dd><a href="http://www.takungpao.com/finance/236132/2020/0302/421697.html" title="﻿行业展望\市场潜力大 规模超4000亿" target="_blank">﻿行业展望\市场潜力大 规模超4000亿</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0302/421697.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>13小时前</dd>
        </dl>
                                <dl class="item clearfix">
                            <dd><a href="http://www.takungpao.com/finance/236132/2020/0302/421695.html" title="﻿专家之见\应用场景多 订製服务有钱途" target="_blank">﻿专家之见\应用场景多 订製服务有钱途</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0302/421695.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>13小时前</dd>
        </dl>
                                <dl class="item clearfix">
                            <dd><a href="http://www.takungpao.com/finance/236132/2020/0302/421693.html" title="﻿机器人如何发挥作用？" target="_blank">﻿机器人如何发挥作用？</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0302/421693.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>13小时前</dd>
        </dl>
                                <dl class="item clearfix">
                <dt><a href="http://www.takungpao.com/finance/236132/2020/0302/421691.html" target="_blank" title="﻿疫情恢复尚有时 无接触服务需求大 机器人配送闯出新商机"><img src="http://img.takungpao.com/2020/0302/20200302042419143.jpg" alt="﻿疫情恢复尚有时 无接触服务需求大 机器人配送闯出新商机"></a></dt>            <dd><a href="http://www.takungpao.com/finance/236132/2020/0302/421691.html" title="﻿疫情恢复尚有时 无接触服务需求大 机器人配送闯出新商机" target="_blank">﻿疫情恢复尚有时 无接触服务需求大 机器人配送闯出新商机</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0302/421691.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>13小时前</dd>
        </dl>
                                <dl class="item clearfix">
                <dt><a href="http://www.takungpao.com/finance/236132/2020/0229/421194.html" target="_blank" title="疫情对中小企业冲击大 港设计和会计等专业服务受拖累"><img src="http://img.takungpao.com/2020/0229/20200229113442105.jpeg" alt="疫情对中小企业冲击大 港设计和会计等专业服务受拖累"></a></dt>            <dd><a href="http://www.takungpao.com/finance/236132/2020/0229/421194.html" title="疫情对中小企业冲击大 港设计和会计等专业服务受拖累" target="_blank">疫情对中小企业冲击大 港设计和会计等专业服务受拖累</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0229/421194.html" target="_blank">受新冠肺炎疫情影响，深圳中小企业受到明显的冲击。戴德梁行28日发布了《疫情对深圳写字楼后市的影响》的报告称，目前仅有33%受访业主称将   </a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公网 李昌鸿</em>前天11:33</dd>
        </dl>
                                <dl class="item clearfix">
                            <dd><a href="http://www.takungpao.com/finance/236132/2020/0229/421130.html" title="﻿基金频道\疫市寻宝 别错过创新企" target="_blank">﻿基金频道\疫市寻宝 别错过创新企</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0229/421130.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>前天04:24</dd>
        </dl>
                                <dl class="item clearfix">
                            <dd><a href="http://www.takungpao.com/finance/236132/2020/0229/421128.html" title="﻿投资人语\击破企业管理六大误解\Anastasia Petraki" target="_blank">﻿投资人语\击破企业管理六大误解\Anastasia Petraki</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0229/421128.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>前天04:24</dd>
        </dl>
                                <dl class="item clearfix">
                <dt><a href="http://www.takungpao.com/finance/236132/2020/0229/421126.html" target="_blank" title="﻿中企协会：纾困财案如及时雨"><img src="http://img.takungpao.com/2020/0229/20200229042409456.jpg" alt="﻿中企协会：纾困财案如及时雨"></a></dt>            <dd><a href="http://www.takungpao.com/finance/236132/2020/0229/421126.html" title="﻿中企协会：纾困财案如及时雨" target="_blank">﻿中企协会：纾困财案如及时雨</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0229/421126.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>前天04:24</dd>
        </dl>
                                <dl class="item clearfix">
                <dt><a href="http://www.takungpao.com/finance/236132/2020/0228/420870.html" target="_blank" title="防疫费入工程造价甘肃高速公路 项目超9成复工入场人员逾17000名"><img src="http://img.takungpao.com/2020/0228/20200228035330428.jpeg" alt="防疫费入工程造价甘肃高速公路 项目超9成复工入场人员逾17000名"></a></dt>            <dd><a href="http://www.takungpao.com/finance/236132/2020/0228/420870.html" title="防疫费入工程造价甘肃高速公路 项目超9成复工入场人员逾17000名" target="_blank">防疫费入工程造价甘肃高速公路 项目超9成复工入场人员逾17000名</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0228/420870.html" target="_blank">近期，甘肃省交通运输行业按照国家和甘肃省“两手抓”决策部署，统筹协调全省公路建设项目复工复产。</a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name"> 杨韶红、刘俊海</em>02-28 15:52</dd>
        </dl>
                                <dl class="item clearfix">
                <dt><a href="http://www.takungpao.com/finance/236132/2020/0228/420831.html" target="_blank" title="国家税务总局将推出24项措施防疫情促发展"><img src="http://img.takungpao.com/2020/0228/20200228100647763.jpg" alt="国家税务总局将推出24项措施防疫情促发展"></a></dt>            <dd><a href="http://www.takungpao.com/finance/236132/2020/0228/420831.html" title="国家税务总局将推出24项措施防疫情促发展" target="_blank">国家税务总局将推出24项措施防疫情促发展</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0228/420831.html" target="_blank">今年从“支持疫情防控帮扶企业纾困解难、推动企业复工复产、服务国家发展战略、优化税收营商环境”等方面推出24项措施。</a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">央视新闻客户端 朱虹 孙蓟潍</em>02-28 10:12</dd>
        </dl>
                                <dl class="item clearfix">
                            <dd><a href="http://www.takungpao.com/finance/236132/2020/0228/420759.html" title="﻿烨星招股 李家杰当基投" target="_blank">﻿烨星招股 李家杰当基投</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0228/420759.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>02-28 04:24</dd>
        </dl>
                                <dl class="item clearfix">
                            <dd><a href="http://www.takungpao.com/finance/236132/2020/0228/420757.html" title="﻿光大水务：22在建项目8个复工" target="_blank">﻿光大水务：22在建项目8个复工</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0228/420757.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>02-28 04:24</dd>
        </dl>
                                <dl class="item clearfix">
                            <dd><a href="http://www.takungpao.com/finance/236132/2020/0228/420755.html" title="﻿百威：首两月中国收入跌22亿" target="_blank">﻿百威：首两月中国收入跌22亿</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0228/420755.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>02-28 04:24</dd>
        </dl>
        
        <dl class="item clearfix">
            <dd><a href="http://www.takungpao.com/finance/236132/2020/0228/420753.html" title="﻿大行料濠赌股估值最少跌30%" target="_blank">﻿大行料濠赌股估值最少跌30%</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0228/420753.html" target="_blank"></a></dd>
            <dd class="sort"><em class="ico"></em><a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a><em class="name">大公报</em>02-28 04:24</dd>
        
        </dl>
        
        <dl class="item clearfix">
            <dt><a href="http://www.takungpao.com/finance/236132/2020/0228/420751.html" target="_blank" 
            title="﻿银娱叹盈利打击大 无意裁员"><img src="http://img.takungpao.com/2020/0228/20200228042408837.jpg" alt="﻿银娱叹盈利打击大 无意裁员"></a>
            </dt>            
            
            <dd><a href="http://www.takungpao.com/finance/236132/2020/0228/420751.html" title="﻿银娱叹盈利打击大 无意裁员" target="_blank">﻿银娱叹盈利打击大 无意裁员</a></dd>
            <dd class="intro"><a href="http://www.takungpao.com/finance/236132/2020/0228/420751.html" target="_blank"></a></dd>
            <dd class="sort">
                <em class="ico"></em>
                <a href="http://www.takungpao.com/finance/236132/index.html" target="_blank">中国经济</a>
                <em class="name">大公报</em>02-28 04:24
            </dd>
        </dl>
        
        <div class="tkp_page"> <a href="/finance/236132/index.html" class="cms_prevpage">上一页</a> <div class="cms_curpage">1</div> <a href="/finance/236132/2.html" class="cms_page">2</a> <a href="/finance/236132/3.html" class="cms_page">3</a> <a href="/finance/236132/4.html" class="cms_page">4</a> <a href="/finance/236132/5.html" class="cms_page">5</a> <a href="/finance/236132/6.html" class="cms_page">6</a> <a href="/finance/236132/7.html" class="cms_page">7</a> <a href="/finance/236132/8.html" class="cms_page">8</a> <a href="/finance/236132/9.html" class="cms_page">9</a> <a href="/finance/236132/10.html" class="cms_page">10</a> <a href="/finance/236132/2.html" class="cms_nextpage">下一页</a></div>
    </div>
'''

# zhongguojingji = 'http://www.takungpao.com/finance/236132/index.html'
zhongguojingji = 'http://www.takungpao.com/finance/236132/2.html'
body = re.get(zhongguojingji).text
# print(body)
doc = html.fromstring(body)
news_list = doc.xpath('//div[@class="wrap_left"]/dl[@class="item clearfix"]')
print(len(news_list))

for news in news_list:
    link = news.xpath('./dd[@class="intro"]/a/@href')[0]
    print(link)

    title = news.xpath("./dd/a/@title")
    print(title[0])


    # source = news.xpath("./dd[@class='sort']/em[@class='name']")[0].text_content()
    # print(source)
    # data = selector.xpath('//div[@id="test1"]/text()').extract()[0]


    pub_date = news.xpath("./dd[@class='sort']/text()")[0]
    # 发布时间的几种处理
    # print(">>> ", pub_date)
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




