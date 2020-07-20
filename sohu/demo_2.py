import json
import time

# _ts = 1595213398000
# # _ts = 1595213834525
# print(_ts)
# print(time.time())
# ret = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(_ts / 1000))
# print(ret)
import requests
from lxml import html

format_url = 'https://v2.sohu.com/integration-api/mix/region/94?\
secureScore=50\
&page=%s\
&size=24\
&pvId=1595213834487tTwv6Ur\
&mpId=0\
&adapter=default\
&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI\
&channel=15\
&requestId=2006120915066717__{}'.format(int(time.time() * 1000))

headers = {
    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
    'cookie': 'SUV=2006120915066717; gidinf=x099980107ee11ac7185448570007cf53d61c5dff4ba; __gads=ID=9bb1261cd25d5ccb:T=1593754903:S=ALNI_MZtjTDJngTMkxi5M1Wu9GisGWKLMw; t=1594459538752; IPLOC=CN4400; _muid_=1595214233823230; MTV_SRC=10010001',
}


def get_list(list_url):
    resp = requests.get(list_url, headers=headers)
    if resp and resp.status_code == 200:
        body = resp.text
        datas = json.loads(body).get("data")
        datas = [data for data in datas if data['resourceType'] == 1]

        for data in datas:
            print(data.get("mobileTitle"))

    print()
    print()


def get_detail(url):


    pass

url1 = 'https://v2.sohu.com/integration-api/mix/region/94?secureScore=50&page=2&size=24&pvId=159522525143916GgmYq&mpId=0&adapter=default&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI&channel=15&requestId=2006120915066717_1595225254182'
url2 = 'https://v2.sohu.com/integration-api/mix/region/94?secureScore=50&page=3&size=24&pvId=159522525143916GgmYq&mpId=0&adapter=default&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI&channel=15&requestId=2006120915066717_1595225257057'
url3 = 'https://v2.sohu.com/integration-api/mix/region/94?secureScore=50&page=4&size=24&pvId=159522525143916GgmYq&mpId=0&adapter=default&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI&channel=15&requestId=2006120915066717_1595225258808'
url4 = 'https://v2.sohu.com/integration-api/mix/region/94?secureScore=50&page=5&size=24&pvId=159522525143916GgmYq&mpId=0&adapter=default&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI&channel=15&requestId=2006120915066717_1595225570222'
url5 = 'https://v2.sohu.com/integration-api/mix/region/94?secureScore=50&page=14&size=24&pvId=159522525143916GgmYq&mpId=0&adapter=default&refer=https%3A%2F%2Ftower.im%2F&spm=smwp.ch15.hdn.2.1580795222633ImxsLrI&channel=15&requestId=2006120915066717_1595225751598'


# url_list = [url1,
#             url2,
#             url3,
#             url4,
#             url5,
#             ]
# for _url in url_list:
#     get_list(_url)

detail_url_list = [
    'https://m.sohu.com/a/408594208_114988',
]

''''
<section id="articleContent" class="article-content">
                        <div class="display-content">
                                <p>每年7月，各地住房公积金政策都会有新一轮调整。截至目前，已经有超过60座城市发布了住房公积金缴存调整方案，其中大多数城市都对缴费基数进行了上调。你今年要缴存的公积金变多了吗？你的公积金账户里还剩多少钱？</p>
<p><strong>1. 上海缴存基数上限上调最大</strong></p>
<p>你具体要缴纳多少公积金，与你所在地的缴存基数和你自己的工资都有关。</p><div class="middle-insert-ad"><a href="javascript:void(0);" data-spm-content="3||844|101.9334_844_828.844_99.rt=87809006c14f92b51d707b8aee7c23b0_flightid=820290_resgroupid=356_materialid=828_itemspaceid=844_saletype=1_loc=CN4401_articleid=%7B%22mpId%22%3A%22408594208%22%7D_suv=2006120915066717_amount=1_plat=8_browser=0_bver=83zzz0_clientip=14zzz152zzz49zzz155_uv=2006120915066717|99|" data-spm-data="3"><div><div id="_3djffcvtlcf" style="width: 100%;"><iframe width="731" frameborder="0" height="217" scrolling="no" src="//pos.baidu.com/s?wid=731&amp;hei=217&amp;di=u3767135&amp;ltu=https%3A%2F%2Fm.sohu.com%2Fa%2F408594208_114988&amp;psi=95064640be989d62ef2b46cd7df21e3f&amp;dc=3&amp;ti=%E5%85%AC%E7%A7%AF%E9%87%91%E6%96%B0%E4%B8%80%E8%BD%AE%E8%B0%83%E6%95%B4%E6%9D%A5%E4%BA%86%EF%BC%8C%E4%BD%A0%E7%9A%84%E8%B4%A6%E6%88%B7%E9%87%8C%E5%AD%98%E4%BA%86%E5%A4%9A%E5%B0%91%E9%92%B1%EF%BC%9F_%E6%89%8B%E6%9C%BA%E6%90%9C%E7%8B%90%E7%BD%91&amp;ps=506x558&amp;drs=3&amp;pcs=1848x946&amp;pss=1848x6987&amp;cfv=0&amp;cpl=3&amp;chi=1&amp;cce=true&amp;cec=UTF-8&amp;tlm=1595215021&amp;psr=1920x1080&amp;par=1863x1057&amp;pis=-1x-1&amp;cja=false&amp;col=zh-CN&amp;cdo=-1&amp;tcn=1595215021&amp;dtm=HTML_POST&amp;tpr=1595215021098&amp;ari=2&amp;ant=0&amp;exps=111000,112027,110011,110053&amp;prot=2&amp;dis=0&amp;dai=2&amp;dri=0"></iframe></div><script assporiginsrc="https://qpb.sohu.com/source/k/common/fxgeg/openjs/ox_c.js" src="https://qpb.sohu.com/source/k/common/fxgeg/openjs/ox_c.js"></script></div></a></div>
<p>每年，各地会综合上一年度职工月平均工资，划定公积金缴存基数的上限和下限，这直接圈定了你缴纳公积金的区间。每人每月具体缴纳的公积金，则要用上一年度月平均工资乘以缴纳比例，根据《住房公积金管理条例》，这个比例不得低于5%。</p>
<p>一般来说，住房公积金是以上一年的7月1日至当年的6月30日为一个年度单位进行调整，在办完6月份的业务后，单位一般会调整员工的公积金缴纳。</p>
<p>据不完全统计，目前已有超过60座城市发布了住房公积金缴存调整方案，其中各地公积金的缴存比例仍维持在5%-12%之间，很多城市都上调了缴费基数的上限，调整缴存基数下限的城市较少，且调整的城市调整幅度也不大。</p>
<p>在我们整理出的25个城市中，仅有黄石、东方两地对上限进行了下调，北京、天津两地未对上限作调整。经过调整后，缴存基数上限最高的是深圳，为31938元；其次是南京，31200元。</p>
                        </div>
                            <div class="lookall-box">
                                    <section id="artLookAll" class="look-all" data-spm-acode="3402" data-spm-click-pm="contentId:408594208;mediaId:114988" data-spm-data="x-1">
                                        <a href="javascript:;" class="surplus-btn" data-spm-data="2"><em>展开剩余</em><em class="hidden-ratio-num">88</em><em>%</em><i class="icon-fold icon"></i></a>
                                    </section>    
                            </div>
                            <div class="hidden-content hide">
                                <p>值得关注的是，北上广深四个一线城市中，仅北京未上调月缴存基数上限。</p>
<p>据上海市公积金管理中心，2020年度上海市住房公积金和补充住房公积金缴存基数上限为28017元，较上一年上调了4521元；深圳和广州也分别上调了4011元和2916元。7月8日，北京住房公积金管理中心发布通知指出，为贯彻进一步降低企业税费负担的政策，降低疫情影响和优化营商环境，不上调月缴存基数上限。</p>
<p>因为缴存基数上限多以各地平均工资的3倍作为基准，缴存基数下限多以各地最低工资为基准，上述调整可以反映出各地平均工资不断上涨，最低工资标准相对稳定。</p>
<p>缴存基数上限的上调影响最大的是收入水平已经超过公积金缴存基数上限的人群，这大多是大企业的高收入群体。大多数地方的缴存基数下限与去年是持平的，这意味着多数中小微企业的公积金成本并未明显上升。</p>
<p><img width="626" height="1764.425714285714" class="content-image" data-src="http://p6.itc.cn/q_70/images03/20200720/8851c97986704f55b34106413a2b94c3.jpeg"></p>
<p>不过，缴存基数的上限只能部分反映出当地上一年度职工月平均工资的情况，却不能反映出地区公积金缴存的具体情况。</p>
<p>从地区缴存情况来看，由于经济发展水平和就业人口数量上的差异，各省之间的缴存总额存在较大差距。一般来说，经济较为发达、人口数量较多的省份，缴存职工的数量更多，当地住房公积金缴存额就会更大。</p>
<p>据近日住建部、财政部、央行联合发布的《全国住房公积金2019年年度报告》，广东、北京、江苏、浙江、上海、山东、四川等7省份2019年公积金缴存额均超千亿，其总和占到2019年全国住房公积金缴存额的52%以上。</p>
<p>但若从和个人关系更为密切的人均缴存额来看，又是另一番境况了。以去年的数据为例，西藏、北京、青海、云南、新疆、天津、浙江公积金人均缴存额最高，2019年每人每月缴存额均超过1500元。</p>
<p>为何上海人均公积金缴存额仅排在全国第10位？ 答案藏在缴存职工的单位性质上。虽然民营企业公积金缴存职工的收入并非都偏低，但为减少企业开支私营企业缴存比例一般都较低，而国家机关和事业单位缴存公积金的比例一般都较高。</p>
<p>根据《上海市住房公积金2019年年度报告》，2019年上海公积金缴存职工中，国家机关和事业单位以及国企仅占20.25%，城镇私营企业及其他城镇企业占比高达56.21%，其次是外商投资企业占16.56%。</p>
<p><img width="626" height="1736.297994269341" class="content-image" data-src="http://p5.itc.cn/q_70/images03/20200720/3b0db60a108741229fe323873610286f.jpeg"></p>
<p><strong>2. 北京、上海单笔贷款额最高</strong></p>
<p>我国住房公积金制度的建立，始于上世纪90年代的城镇住房体制改革，通过企业和个人共同储蓄，为购房职工发放低息贷款，进而提高居民住房消费的意愿和能力。</p>
<p>1991年，这一制度最早于在上海进行试点，随后扩大到北京、天津、南京等城市。1994年，国务院印发《关于深化城镇住房制度改革的决定》，提出在全国范围内全面推行住房公积金制度。此后，这一制度体系不断完善。</p>
<p>《全国住房公积金2019年年度报告》显示，截至2019年末，全国住房公积金累计缴存总额169607.66亿元，提取总额104235.23亿元，发放住房公积金个人住房贷款3620.88万笔97959.46亿元，向373个试点项目发放贷款872.15亿元，住房公积金发挥的作用不言而喻。</p>
<p>从住房公积金近年的缴存情况来看，实缴单位、实缴职工、人均年缴存额以及缴存余额均不断提升。截至2019年末，住房公积金制度已覆盖全国近1.5亿人。</p>
<p><img width="626" height="1091.922857142857" class="content-image" data-src="http://p8.itc.cn/q_70/images03/20200720/8784c0d916874350b0b7316e37f42216.jpeg"></p>
<p>缴存的公积金数额在逐年上升，花出去的公积金也是一样。</p>
<p>截至2019年末，缴存余额扣除个人住房贷款余额、保障性住房建设试点项目贷款余额和国债余额后，全国住房公积金结余9461.52亿元，留下来的钱也就占累计缴存的5.6%而已。</p>
<p>数据显示，近年全国住房公积金提取人数和提取总额呈上升趋势。2019年，住房公积金的提取额已经占到当年缴存额的68%以上；住房公积金提取人数超过5648万，占实缴职工人数的三分之一以上。</p>
<p>从用途来看，提取的公积金大多用在了偿还购房贷款本息上。2019年，有超过3100万人提取了公积金偿还购房贷款本息，占提取总人数的55%以上；这一用途的提取金额超过7500亿元，占提取总额的46%以上。</p>
<p>2019年，全国发放住房公积金个人住房贷款286.04万笔，比上年增长13.25%；发放金额12139.06亿元，比上年增长18.79%。截至2019年末，个人住房贷款余额占到年度末住房公积金缴存余额的85%以上。</p>
<p><img width="626" height="983.7142857142857" class="content-image" data-src="http://p5.itc.cn/q_70/images03/20200720/ceae16ba59b44002b3e249dce1eb4292.jpeg"></p>
<p>从各地职工的提取情况来看，青海、云南、辽宁、广西等地2019年住房公积金提取率较高，其中青海住房公积金的提取额已经占到当年缴存额的80%以上；西藏、陕西、山西、湖南、上海等地提取率较低，均未超过60%。</p>
<p>从各地职工的贷款情况来看，2019年贷款发放额和放贷比数最高的是江苏、广东和上海，2019年贷款发放总额分别为1226.04亿元、1173.83亿元和939.18亿元。若从单笔贷款额来看，排在前面的是北京、上海、西藏、广东和福建，这几个地区2019年发放的单笔贷款额均在50万元以上。</p>
<p>若以个贷率（个人公积金贷款余额占年末住房公积金缴存余额的比率）来衡量公积金住房贷款的使用力度，2019年全国12个省份个贷率超过了85%的警戒线，公积金余额趋紧；其中，重庆、安徽、江苏、贵州、浙江更是超过了95%，住房公积金贷款用于支持职工购房的力度较大。</p>
<p>若从个人住房消费类提取额和个人住房贷款发放额占当年缴存额的比例看各地公积金对个人住房使用的贡献，青海、江苏、贵州、甘肃、宁夏等地贡献率最高，2019年住房消费类提取额和贷款发放额占当年缴存额的比例均超过115%；北京、河南、河北、四川等地贡献率最低，2019年住房消费类提取额和贷款发放额占当年缴存额的比例均在100%以下。</p>
<p><img width="626" height="1847.5942857142857" class="content-image" data-src="http://p4.itc.cn/q_70/images03/20200720/78cdc19004c24748a3903dbe1dc7f5e1.jpeg"></p>
<p><strong>3. 公积金存废：社会效益与不足兼有</strong></p>
<p>今年，新冠肺炎疫情对经济造成一定冲击，住房公积金的存废再次成为舆论焦点之一。</p>
<p>中国国际经济交流中心副理事长、重庆市原市长黄奇帆在2月发表的一篇文章中提到，为了解决企业复工复产的重重困难，可以考虑取消企业住房公积金制度，一石激起千层浪，附和与反对的声音此起彼伏。</p>
<p>不可否认的是，住房公积金制度在支持居民购房上还是做出一定贡献的。</p>
<p>从绝对数量来看，如前所述，住房公积金制度惠及职工数量持续增长，截至2019年底已覆盖全国近1.5亿人。</p>
<p>从支持对象来看，住房公积金制度重点支持中、低收入群体首套普通住房。2019年发放的个人住房贷款笔数中，中、低收入职工贷款占95.41%，首套住房贷款占86.96%，144平方米（含）以下住房贷款占90.58%。</p>
<p>从支持项目来看，对租赁住房消费和保障性住房建设支持的力度不小。2019年，住房租赁提取金额937.83亿元，比上年增长28.4%，占当年提取金额的比例逐年上涨。截至2019年末，累计为城市公共租赁住房（廉租住房）建设提供补充资金3958.86亿元。</p>
<p>从节约利息来看，住房公积金个人住房贷款利率比同期商业性个人住房贷款基准利率低1.65-2个百分点，2019年发放的住房公积金个人住房贷款，偿还期内可为贷款职工节约利息支出2617.14亿元，平均每笔贷款可节约利息支出9.13万元。</p>
<p><img width="626" height="1480.9371428571428" class="content-image" data-src="http://p9.itc.cn/q_70/images03/20200720/016c569bd40048b7a67ae074129bbed7.jpeg"></p>
<p>但同样不容忽视的是，住房公积金制度在普适性上仍面临一些问题。</p>
<p>从企业性质来看，2018年城镇私营企业及其他城镇企业公积金实缴职工人数为4904.9万人，占各类单位实缴职工人数的32.96%，低于国家机关和事业单位、国有企业49.45%的占比。由于私营部门就业人数远高于国有部门，私有部门就业人员缴纳公积金的比例就更是低于国有部门了。</p>
<p>从房贷市场来看，住房公积金个人住房贷款市场占有率一直不高，且近年还呈现出下降的趋势，2019年末住房公积金个人住房贷款市场占有率仅为15.61%，远低于商业贷款。</p>
<p><img width="626" height="958.6742857142857" class="content-image" data-src="http://p8.itc.cn/q_70/images03/20200720/e4597e542a944c1196840712883a3020.jpeg"></p>
<p>今年5月，中共中央、国务院发布《关于新时代加快完善社会主义市场经济体制的意见》中明确提到要加快建立多主体供给、多渠道保障、租购并举的住房制度，改革住房公积金制度。由此看来，如何配合房地产制度进行调整，是未来住房公积金制度改革应该思考的方向。</p>
<p>数据新闻编辑 李媛</p>
<p>新媒体设计 陈冬</p>
<p>校对 李立军</p>
<div id="transferArticle"></div>
    <!-- 标签展示，数据最多返回10个 -->
    <footer class="footer-tag-state">
                    <div id="newStatement"><div data-v-0c0d5b2c="" class="statement-container type-1"><!----> <span data-v-0c0d5b2c="" class="state-title"><i data-v-0c0d5b2c="" class="icon icon-state"></i>平台声明</span> <!----> <!----></div></div>
    </footer>
    <div class="statement"></div>

                            </div>
                    </section>
'''

for url in detail_url_list:
    print(url)
    page = requests.get(url, headers=headers).text
    # print(page)
    doc = html.fromstring(page)
    content = doc.xpath(".//section[@id='articleContent']")[0]
    print(content)
    print(content.text_content())








