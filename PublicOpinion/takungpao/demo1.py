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
url = 'http://finance.takungpao.com/hkstock/cjss/index_4.html'
body = re.get(url).text
items = parse_list(body)
print(pprint.pformat(items))
print(len(items))




'''
<div class="m_txt_news">
<ul>
    <li>
        <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481902.html" target="_blank" class="a_time txt_blod">2017-08-10</a>
        <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481902.html" target="_blank" class="a_title txt_blod">震灾刺激建筑股走强</a>
    </li>
    
    <li>
        <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481892.html" target="_blank" class="a_time">2017-08-10</a>
        <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481892.html" target="_blank" class="a_title">旭辉：全年销售或破千亿</a>
    </li>
    
    <li>
        <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481890.html" target="_blank" class="a_time">2017-08-10</a>
        <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481890.html" target="_blank" class="a_title">九仓分拆收租物业 股价飙14%</a>
    </li>

    <li>
        <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481888.html" target="_blank" class="a_time">2017-08-10</a>
        <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481888.html" target="_blank" class="a_title">﻿金管局增发票据 港汇劲弹</a>
    </li>
    
    <li>
        <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481887.html" target="_blank" class="a_time">2017-08-10</a>
        <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481887.html" target="_blank" class="a_title">上半年日均成交增近三成</a>
    </li>
</ul>

<ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481886.html" target="_blank" class="a_time txt_blod">2017-08-10</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481886.html" target="_blank" class="a_title txt_blod">大摩指港交所现价估值过高</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481883.html" target="_blank" class="a_time">2017-08-10</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481883.html" target="_blank" class="a_title">李小加：港交所不会咬错人</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481882.html" target="_blank" class="a_time">2017-08-10</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481882.html" target="_blank" class="a_title">腾讯撑大局 恒指跌势减</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481604.html" target="_blank" class="a_time">2017-08-09</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481604.html" target="_blank" class="a_title">港交所上半年收入同比增长10% 沪深港通增长势头持续</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481591.html" target="_blank" class="a_time">2017-08-09</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481591.html" target="_blank" class="a_title">“辉哥”借壳 大庆乳业变火锅股</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481589.html" target="_blank" class="a_time txt_blod">2017-08-09</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481589.html" target="_blank" class="a_title txt_blod">许家印再成地产首富！内房股暴涨的深层原因</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481579.html" target="_blank" class="a_time">2017-08-09</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481579.html" target="_blank" class="a_title">开盘：沪指跌0.12% 钢铁股萎靡</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481528.html" target="_blank" class="a_time">2017-08-09</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481528.html" target="_blank" class="a_title">《战狼2》大卖 高层减持套现3000万</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481527.html" target="_blank" class="a_time">2017-08-09</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481527.html" target="_blank" class="a_title">叶茂林：恒指今年料上32000</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481525.html" target="_blank" class="a_time">2017-08-09</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481525.html" target="_blank" class="a_title">腾讯领军 港股3连升逼28000</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481508.html" target="_blank" class="a_time txt_blod">2017-08-09</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481508.html" target="_blank" class="a_title txt_blod">万达酒店发展9日早临时停牌 此前否认出售澳洲资产</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481504.html" target="_blank" class="a_time">2017-08-09</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3481504.html" target="_blank" class="a_title">真跌还是假升？</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3479602.html" target="_blank" class="a_time">2017-08-03</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3479602.html" target="_blank" class="a_title">﻿62年长情“打工王”</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3479604.html" target="_blank" class="a_time">2017-08-03</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3479604.html" target="_blank" class="a_title">﻿渣打拒派中期息外围泻6%　净息差扩阔贷款续增</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3479283.html" target="_blank" class="a_time">2017-08-02</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3479283.html" target="_blank" class="a_title">﻿澳门赌收飙29%连升12月 瑞信看好首选银娱金沙</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3479282.html" target="_blank" class="a_time txt_blod">2017-08-02</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3479282.html" target="_blank" class="a_title txt_blod">﻿港付货人委会推航运课程</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3479281.html" target="_blank" class="a_time">2017-08-02</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-08/3479281.html" target="_blank" class="a_title">﻿卡宾网上销售大增三成</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3470548.html" target="_blank" class="a_time">2017-07-06</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3470548.html" target="_blank" class="a_title">撬动供应链金融蓝海 盛业资本成功登陆港交所</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3470122.html" target="_blank" class="a_time">2017-07-05</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3470122.html" target="_blank" class="a_title">人民网两度批《王者荣耀》 腾讯市值日失千亿</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469757.html" target="_blank" class="a_time">2017-07-04</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469757.html" target="_blank" class="a_title">﻿恒大上月销售611亿 赎回全部永续债</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469754.html" target="_blank" class="a_time txt_blod">2017-07-04</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469754.html" target="_blank" class="a_title txt_blod">﻿罗兵咸料港今年IPO保三甲 纽交所暂列全球IPO首位</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469363.html" target="_blank" class="a_time">2017-07-03</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469363.html" target="_blank" class="a_title">﻿A股下半年维持强者恒强格局 关注白马行情扩散机会</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469361.html" target="_blank" class="a_time">2017-07-03</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469361.html" target="_blank" class="a_title">香港迎来新一个黄金二十年 金融业将呈突破发展</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469354.html" target="_blank" class="a_time">2017-07-03</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469354.html" target="_blank" class="a_title">﻿恒指料挑战今年高位 腾祺基金看好后市见二万七</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469353.html" target="_blank" class="a_time">2017-07-03</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-07/3469353.html" target="_blank" class="a_title">岳毅：债券通为债券市场和人民币发展增添新动力</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3465690.html" target="_blank" class="a_time txt_blod">2017-06-28</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3465690.html" target="_blank" class="a_title txt_blod">盛业资本公开发行1.85亿股 预期7月6日上市</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3465311.html" target="_blank" class="a_time">2017-06-27</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3465311.html" target="_blank" class="a_title">港上半年IPO额退至全球第四 劲投招股5555元入场</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3458154.html" target="_blank" class="a_time">2017-06-06</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3458154.html" target="_blank" class="a_title">Nexion申请香港创业板挂牌 今起招股入场费2778元</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3457761.html" target="_blank" class="a_time">2017-06-05</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3457761.html" target="_blank" class="a_title">A股"入摩"概率增大港股现蠢动 中资背景证券股值博</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3456909.html" target="_blank" class="a_time">2017-06-02</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3456909.html" target="_blank" class="a_title">周生生：预计今年零售市场持平 年内或再关两家分店</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3456512.html" target="_blank" class="a_time txt_blod">2017-06-01</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-06/3456512.html" target="_blank" class="a_title txt_blod">宝威获金沙江资本入股 认购8.76亿股集资1.57亿港元</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3456113.html" target="_blank" class="a_time">2017-05-31</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3456113.html" target="_blank" class="a_title">北水进场恒指逼近二万六 ﻿内房或续上专家吁吸落后股</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3455028.html" target="_blank" class="a_time">2017-05-27</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3455028.html" target="_blank" class="a_title">﻿港金管局前总裁任志刚:若再现金融风暴刹伤力将更大</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3454646.html" target="_blank" class="a_time">2017-05-26</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3454646.html" target="_blank" class="a_title">天合化工再遭港证监叫停受查 停牌逾两年或难翻身</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3454238.html" target="_blank" class="a_time">2017-05-25</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3454238.html" target="_blank" class="a_title">﻿香港证监会：正调查大量个案 涉上市公司高管失职</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3453919.html" target="_blank" class="a_time txt_blod">2017-05-24</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3453919.html" target="_blank" class="a_title txt_blod">金山软件Q1营收12.13亿元 网游营收8.17增长79%</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3453458.html" target="_blank" class="a_time">2017-05-23</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3453458.html" target="_blank" class="a_title">第一视频拓金融股价飙近六成 现金充足未来或再并购</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3453074.html" target="_blank" class="a_time">2017-05-22</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3453074.html" target="_blank" class="a_title">近一个月港股通净流入365.71亿元 “南热北冷”持续</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3452238.html" target="_blank" class="a_time">2017-05-19</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3452238.html" target="_blank" class="a_title">长港敦信因业绩及配股配债公布存在重大失实被停牌</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3452262.html" target="_blank" class="a_time">2017-05-18</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3452262.html" target="_blank" class="a_title">阿里健康年度亏损扩大9.36%至2.08亿元 不派末期息</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3451448.html" target="_blank" class="a_time txt_blod">2017-05-17</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3451448.html" target="_blank" class="a_title txt_blod">圆通购先达国际六成股份 否认借壳强调进军国际业务</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3451072.html" target="_blank" class="a_time">2017-05-16</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3451072.html" target="_blank" class="a_title">尚捷集团再次启动IPO路径:发售全改变 包销商大洗牌</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3450666.html" target="_blank" class="a_time">2017-05-15</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3450666.html" target="_blank" class="a_title">﻿港股市值20年来上涨近八倍 两千家上市公司中资占半</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3449808.html" target="_blank" class="a_time">2017-05-12</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3449808.html" target="_blank" class="a_title">﻿瑞声遭狙击插10%失守红底 沽空机构料股价跌至40元</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3449392.html" target="_blank" class="a_time">2017-05-11</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3449392.html" target="_blank" class="a_title">李泽鉅：暂不考虑重提电能长建合并 或细拆长建股份</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3448985.html" target="_blank" class="a_time txt_blod">2017-05-10</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3448985.html" target="_blank" class="a_title txt_blod">﻿杉杉旗下富银融资租赁招股筹1.44亿 入场费3777元</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3448620.html" target="_blank" class="a_time">2017-05-09</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3448620.html" target="_blank" class="a_title">圆通加速国际化布局 拟10.4亿港元控股先达国际物流</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3448265.html" target="_blank" class="a_time">2017-05-08</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3448265.html" target="_blank" class="a_title">港股五月走势聚焦内地经济 五连跌后短线或技术反弹</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3447525.html" target="_blank" class="a_time">2017-05-05</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3447525.html" target="_blank" class="a_title">交银国际拟全球发售6.67亿股 五名基投涉6.45亿元</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3447158.html" target="_blank" class="a_time">2017-05-04</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3447158.html" target="_blank" class="a_title">汇控季绩前瞻：市场预计税前盈利逾400亿少赚13%</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3446815.html" target="_blank" class="a_time txt_blod">2017-05-03</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3446815.html" target="_blank" class="a_title txt_blod">传日清拟分拆内地及香港业务赴港上市 集资两亿美元</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3446824.html" target="_blank" class="a_time">2017-05-02</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-05/3446824.html" target="_blank" class="a_title">﻿退欧前路多变朝核风云诡谲 港股“五穷月”危机四伏</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3446825.html" target="_blank" class="a_time">2017-04-28</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3446825.html" target="_blank" class="a_title">﻿香港证监会:第三板咨询与创业板检讨咨询应同步推出</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3445171.html" target="_blank" class="a_time">2017-04-27</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3445171.html" target="_blank" class="a_title">港交所望沙特阿美成新股通头炮 李小加:两者天生一对</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3444775.html" target="_blank" class="a_time">2017-04-26</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3444775.html" target="_blank" class="a_title">﻿丰盛控股遭沽空狙击暴跌后停牌 全系市值蒸发87亿元</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3444408.html" target="_blank" class="a_time txt_blod">2017-04-25</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3444408.html" target="_blank" class="a_title txt_blod">消息称众安保险拟三季度在港挂牌上市 集资20亿美元</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3444030.html" target="_blank" class="a_time">2017-04-24</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3444030.html" target="_blank" class="a_title">沪深港通开通后南下资金超4千亿 港股吸引力再凸显</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3443263.html" target="_blank" class="a_time">2017-04-21</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3443263.html" target="_blank" class="a_title">﻿美图主席儿子减持套现356万港元 持股量降至5.99%</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3442889.html" target="_blank" class="a_time">2017-04-20</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3442889.html" target="_blank" class="a_title">﻿内资撤退港股三日挫487点 二万四成向上突破阻力位</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3442521.html" target="_blank" class="a_time">2017-04-19</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3442521.html" target="_blank" class="a_title">﻿光大绿色环保周五招股 入场费5959元最多集资33亿</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3442189.html" target="_blank" class="a_time txt_blod">2017-04-18</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3442189.html" target="_blank" class="a_title txt_blod">中国神华首季煤炭销量同比增22.5% 售电量亦增9.1%</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3441270.html" target="_blank" class="a_time">2017-04-14</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3441270.html" target="_blank" class="a_title">﻿内房股发威富力越地破顶 恒指继续横行走势欠缺方向</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3440917.html" target="_blank" class="a_time">2017-04-13</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3440917.html" target="_blank" class="a_title">建滔积层板遭母公司建滔化工减持 复牌股价挫半成</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3440583.html" target="_blank" class="a_time">2017-04-12</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3440583.html" target="_blank" class="a_title">中再生：河南风电项目明年启用 料限电情况逐步纾缓</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3440303.html" target="_blank" class="a_time">2017-04-11</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3440303.html" target="_blank" class="a_title">国泰君安证券H股正式挂牌交易 债券通服务紧跟市场</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3439912.html" target="_blank" class="a_time txt_blod">2017-04-10</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3439912.html" target="_blank" class="a_title txt_blod">美联储缩表速度受关注 港股牛皮待变或挑战24800点</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3439187.html" target="_blank" class="a_time">2017-04-07</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3439187.html" target="_blank" class="a_title">海天能源:未来有意收购更多水电站 望年内转主板上市</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3438823.html" target="_blank" class="a_time">2017-04-06</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3438823.html" target="_blank" class="a_title">﻿苏创燃气洽购华东项目 将研究收购海外燃气企业机会</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3438468.html" target="_blank" class="a_time">2017-04-05</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3438468.html" target="_blank" class="a_title">﻿中国新高教今起招股 入场费3252元集资额逾9亿</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3437459.html" target="_blank" class="a_time">2017-04-01</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-04/3437459.html" target="_blank" class="a_title">﻿港股首季报捷累涨2111点 中海油跌4.3%创蓝筹最差</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3437149.html" target="_blank" class="a_time txt_blod">2017-03-31</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3437149.html" target="_blank" class="a_title txt_blod">﻿中国通号去年多赚22%末期息0.1元 内地市场订单增</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3436778.html" target="_blank" class="a_time">2017-03-30</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3436778.html" target="_blank" class="a_title">招商局港口核心溢利增25%多赚55亿 每股派65港仙</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3436389.html" target="_blank" class="a_time">2017-03-29</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3436389.html" target="_blank" class="a_title">上市半日即遭停牌 骏杰集团复牌暴跌逾8成变毫子股</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3436032.html" target="_blank" class="a_time">2017-03-28</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3436032.html" target="_blank" class="a_title">﻿调控震散内房港股挫164点 花旗升恒指目标至25500</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3435660.html" target="_blank" class="a_time">2017-03-27</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3435660.html" target="_blank" class="a_title">﻿深港通令港股通成功升级 内地机构持仓港股意愿上升</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3433818.html" target="_blank" class="a_time txt_blod">2017-03-24</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3433818.html" target="_blank" class="a_title txt_blod">﻿中移动腾讯捱沽内房股全线向上 恒指震荡待外围利好</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3433467.html" target="_blank" class="a_time">2017-03-23</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3433467.html" target="_blank" class="a_title">﻿内银股遭投资者抛售港股终止四连涨 夜期转升145点</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3433071.html" target="_blank" class="a_time">2017-03-22</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3433071.html" target="_blank" class="a_title">﻿港灯去年赚36亿近持平 天然气比例升燃料成本势上升</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3432705.html" target="_blank" class="a_time">2017-03-21</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3432705.html" target="_blank" class="a_title">港交所：年内将检讨创业板监管问题并咨询市场意见</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3432344.html" target="_blank" class="a_time">2017-03-20</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3432344.html" target="_blank" class="a_title">港交所今日正式推出人民币期权 可提高场内交易效率</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3431542.html" target="_blank" class="a_time txt_blod">2017-03-17</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3431542.html" target="_blank" class="a_title txt_blod">﻿66只熊证"打靶"北水左右升势 港股四月或扑25000点</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3431141.html" target="_blank" class="a_time">2017-03-16</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3431141.html" target="_blank" class="a_title">﻿花旗上调创科实业目标价至36.5元 维持“买入”评级</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3430754.html" target="_blank" class="a_time">2017-03-15</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3430754.html" target="_blank" class="a_title">361度去年纯利4.03亿同比下跌22% 净利润跌近12%</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3430366.html" target="_blank" class="a_time">2017-03-14</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3430366.html" target="_blank" class="a_title">华润水泥去年多赚三成 周龙山:今年销量升幅可达3%</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3430005.html" target="_blank" class="a_time">2017-03-13</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3430005.html" target="_blank" class="a_title">美国今年加息次数预期不定 港股或下试二万三关口</a>
</li>
        </ul>
                                                                        <ul>
        <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3429132.html" target="_blank" class="a_time txt_blod">2017-03-10</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3429132.html" target="_blank" class="a_title txt_blod">﻿民生教育今起招股 3070元入场最多集资15.2亿元</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3428759.html" target="_blank" class="a_time">2017-03-09</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3428759.html" target="_blank" class="a_title">﻿内房股井喷港股今年首现"死亡交叉" 世茂涨幅超一成</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3428366.html" target="_blank" class="a_time">2017-03-08</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3428366.html" target="_blank" class="a_title">﻿美高域超购1176倍今挂牌 暗盘报1.7元高上市价16%</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3428005.html" target="_blank" class="a_time">2017-03-07</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3428005.html" target="_blank" class="a_title">﻿港股通标的股调整 恒指反弹乏力八连阴成交量急缩</a>
</li>
                                                            <li>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3427592.html" target="_blank" class="a_time">2017-03-06</a>
    <a href="http://finance.takungpao.com/hkstock/cjss/2017-03/3427592.html" target="_blank" class="a_title">东北虎药业年度净利为25.5万元 同比大跌96.41%</a>
</li>
        </ul>
                    </div>

'''
