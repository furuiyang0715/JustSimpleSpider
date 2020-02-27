# -*- coding: utf-8 -*-

import json
import re

import requests as req
from lxml import html

from PublicOpinion.cls_cn.cls_base import ClsBase


class Reference(ClsBase):
    def __init__(self, num):
        super(Reference, self).__init__()
        self.num = num
        self.base_url = 'https://www.cls.cn/reference/{}'
        self.page_url = self.base_url.format(self.num)
        self.table = 'cls_depth_theme'
        self.fields = ['title', 'link', 'pub_date', 'article']

    def _parse_list_page(self, page):
        try:
            json_data = re.findall(r'__NEXT_DATA__ = (\{.*\})', page)[0]
            py_data = json.loads(json_data)
            news_list = py_data.get('props', {}).get('initialState', {}).get('reference', {}).get('morningNewsList')
        except:
            return None

        return news_list

    def _parse_app_page(self, link):
        '''

        <div class="content">
                        <p><strong>一、【财联社2月14日早间新闻精选】</strong></p><p><strong>宏观新闻：</strong></p><p>1、国家主席习近平13日晚应约同马来西亚总理马哈蒂尔通电话。习近平强调，我们一定能把疫情影响降到最低，保持中国经济发展势头，努力实现今年发展目标任务，同时继续朝我们的长远目标坚定迈进。</p><p>2、中央应对新冠肺炎疫情工作领导小组会议指出，要继续把湖北省特别是武汉市作为疫情防控的重中之重。通过错峰等措施今年不会出现往年那样的返程高峰。抓紧投放临床有效药物，提高治愈率、降低病亡率。</p><p>3、据国家卫健委数据统计，2月12日0—24时，全国新增确诊病例15152例，累计59804例。全国除湖北以外地区新增确诊病例312例，连续第9日呈下降态势。</p><p>4、国际货币基金组织总裁格奥尔基耶娃表示，IMF正在收集数据以评估新冠肺炎疫情的全面影响。她认为，中国经济最有可能出现的情况是“V型”增长。</p><p><strong>行业新闻：</strong></p><p>1、日前，中共中央决定，应勇同志任湖北省委委员、常委、书记，蒋超良同志不再担任湖北省委书记、常委、委员职务。</p><p>2、财政部印发通知，明确医疗卫生机构开展疫情防控工作所需的防护、诊断和治疗专用设备以及快速诊断试剂采购所需经费由地方财政予以安排，中央财政视情给予补助。</p><p>3、2月13日全国铁路预计发送旅客100万人次，同比减少91.9%。</p><p>4、MSCI官方表示，科创板需实现陆股通交易资格方可纳入MSCI中国指数，目前该指数中也并无科创板股票。京沪高铁和金山办公因不满足陆股通资格未纳入MSCI中国指数。</p><p>5、特斯拉向美国证券交易委员会提交的文件显示，2019年其在中国区实现营收29.79亿美元，同比增长69.55%。</p><p>6、市场监管总局要求进一步加快药品、医疗器械等应急审批，全力支持疫情防控有效药品、疫苗研发；加快生产符合国家标准的医用口罩和防护服等防护用品。</p><p>7、广东省印发《广东省加快半导体及集成电路产业发展的若干意见》，提到加大财政支持力度。设立省半导体及集成电路产业投资基金，鼓励有条件的地市设立集成电路产业投资基金，出台产业扶持政策。</p><p>8、我国三代核电技术“华龙一号”在英国的通用设计审查（GDA）第三阶段工作完成，正式进入第四阶段，即最终批准阶段。</p><p>9、近日，国务院扶贫开发领导小组印发通知，强调要坚定信心决心，坚持如期全面完成脱贫攻坚任务不动摇，工作总体安排部署不能变，决不能有缓一缓、等一等的思想。</p><p>10、中注协正与有关部门密切沟通，并致函有关部门，提请研究年度报告披露延期问题。</p><p>11、中汽协称，目前没有明确考虑需要汽车刺激政策。1月份，我国汽车产销同比分别下降24.6%和18.0%。1月份新能源汽车销量同比下降54.5%。</p><p>12、国务院联防联控发布会透露，截止到2月11日，全国口罩产能利用率已经达到94%，特别是一线防控急需的医用n95口罩，产能利用率达到了128%。</p><p>13、比特币价格已连续3日居于10000美元之上，昨日触及10500美元。</p><p>14、中国生物经过严格的血液生物安全性检测，病毒灭活，抗病毒活性检测等，已成功制备出用于临床治疗的特免血浆。</p><p><strong>公司新闻：</strong></p><p>1、阿里巴巴2020财年第三财季营收1614亿元，市场预期1592亿元。阿里巴巴晚间在业绩发布会上表示，淘宝、天猫、本地生活服务也可能会出现收入增长为负。</p><p>2、恒大集团宣布，自签署《商品房买卖合同》之日起至5月10日，购房者享有最低价购房权益，如购买楼盘价格下调，可获补差价。</p><p>3、北上资金昨天净流入7.91亿元。沪股通方面，上海机场净买入2.38亿，华友钴业净买入2.27亿。深股通方面，天齐锂业净买入5.53亿，五粮液净买入2.58亿。</p><p>4、小米公司正式发布年度旗舰小米10系列。小米10系列首发骁龙865旗舰平台，并采用一亿像素8K超清相机以及对称式立体声。小米10系列售价3999元起，将于2月14日正式上市。</p><p>5、中信证券发布2020年1月份财务数据简报，母公司1月实现净利润8.6亿元，去年同期为7.4亿元。</p><p>6、连续两日涨停的博瑞医药公告，公司于近日成功仿制开发了瑞德西韦原料药合成工艺技术和制剂技术。公司关于瑞德西韦的开发工作尚处于研发阶段，不存在侵犯专利权的情形。</p><p>7、盘龙药业公告，公司股东苏州永乐九鼎等股东拟合计减持公司股份不超过520万股（占公司总股本比例6%）。</p><p>8、陇神戎发公告，公司拟变更经营范围，将口罩、防护服、消毒液、测温仪等生产和销售纳入经营范围。</p><p>9、易见股份公告，公司股东九天控股拟将其持有的易见股份2.02亿股无限售流通股份（占公司总股本的18.00%）转让给工投君阳。</p><p><strong>环球市场：</strong></p><p>美股三大股指集体小幅收跌 特斯拉涨超4%</p><p>美东时间周四，美国三大股指集体小幅收跌，其中道指跌0.43%，纳指跌0.14%，标普500指数跌0.16%。特斯拉收涨4.78%。阿里巴巴收跌1.6%，此前预计本季度营收增速会放缓。美国黄金期货收涨0.46%。WTI原油期货收涨0.49%，布伦特原油收涨0.99%。</p><p><strong>二、【投资机会参考】</strong></p><p><strong>1、【开工延迟 维生素价格飙升30%】</strong></p><p>中国饲料行业信息网数据显示，节后欧洲VE报价6.5至8欧元/公斤，贸易商出口报价涨至7至8美元/公斤，较节前上涨30%；VD3欧洲市场报价涨至9至11.5欧元/公斤；VA市场报价涨至64至67欧元/公斤。</p><p>中国是全球维生素生产大国，国内近6成维生素出口国外。受疫情影响国内维生素企业开工推后，导致全球维生素供应紧张。一方面海外库存低、需求稳定，另一方面国内为保障民生饲料需求受疫情影响相对有限，因此维生素行业整体供需偏紧。2月5日发布的中央一号文件，再为维生素产业的升温加了“一把火”。文件要求2020年加快恢复生猪生产，而生猪、能繁母猪存栏量的上升，有助于拉动国内猪饲料需求。分析人士认为，作为猪饲料重要添加剂，维生素需求将稳步提升。</p><p>A股上市公司中，花园生物（300401）全球VD3龙头企业，市场份额约占30%。金达威（002626）维生素A产能2700吨左右，维生素D3产能1000吨左右。</p><p><strong>2、【快车道又现一批黑马 氢燃料电池汽车政策或“呼之欲出”】</strong></p><p>“推动充电、加氢等设施建设”去年首次写入《政府工作报告》，开启燃料电池的“元年”。据悉，2020年各地将合计推广5000台左右燃料电池车，总保有量或将在年底达到1万台。此外，制氢、储氢和运氢三大成本难题有望在《新能源汽车产业发展规划（2021-2035年）》，以及即将出台的国家级氢燃料电池汽车专项规划中得到逐步解决。</p><p>机构预计，2020年燃料电池汽车补贴政策值得期待。目前我国氢燃料电池汽车保有量已经超过6000辆，根据战略目标，2020年达到1万辆燃料电池运输车辆，2030年达到200万辆燃料电池运输车辆。据测算，2030、2050年氢燃料电池汽车市场空间分别突破3000亿、7000亿，系统关键零部件市场空间突破2000亿、3000亿，氢燃料电池+系统市场空间有望在2050年突破万亿。同时随着氢燃料电池汽车产业化的成熟，未来在船舶、无人机等交通领域以及储能、电力等民生领域有望开创更多应用场景。</p><p>公司方面，雄韬股份（002733）未来三年拟投放1800辆氢能源物流车，公司多座加氢站已经开工建设并于近期开始运营。雪人股份（002639）已布局氢气制取与加氢站建设运营设备以及氢燃料电池发动机系统集成，包括燃料电池电堆、燃料电池空压机及氢气循环泵等。</p><p><strong>3、【用户在线数几倍增长 或将成为云经济相关产业触发点】</strong></p><p>疫情促使远程办公、在线教育、在线医疗、远程算力开放等互联网在线应用近期业务量大增，相关公司的用户在线数同比几倍增长。2月3日复工首日，阿里钉钉和企业微信均出现访问量过大导致无法访问的问题，两家公司不得不先后扩容10多万台服务器应对高峰。截至2月11日，AppStore免费排行榜中，阿里钉钉仍然稳居第一，腾讯会议和企业微信紧随其后。</p><p>疫情已经成为云经济相关产业一个事件性的触发点，有望加速整个行业的发展。机构认为，流量经济和云基础设施成为2020年上半年最确定的高增长行业。应对在线流量爆发，阿里云、腾讯云和华为云紧急扩容，在5G和在线视频需求增长下，2020年云计算基础设施重回高增长，根据IDC预测2023年中国X86服务器市场规模将达到292.85亿美元，2020-2023年复合增长率将达到11.9%。</p><p>A股上市公司中，中科曙光（603019）依托自主云计算产品，牵头和参与制定的多个云计算国家标准完成了标准草案制定。先进数通（300541）主要业务领域均围绕云计算相关产品及解决方案展开，包括：云数据中心建设与运维、金融交易云、大数据相关解决方案等。</p><p><strong>4、【特斯拉拟在中国生产长续航后轮驱动版Model 3 正寻求监管机构批准】</strong></p><p>据路透报道，一份政府文件显示，特斯拉正在寻求中国监管机构的批准，以生产国产长续航后轮驱动版Model 3。知情人士表示，相较于标准Model 3 400多公里的续航里程，新版本将拥有更长的续航能力，并且为后轮驱动。</p><p>国产化后的特斯拉Model3补贴后售价为29.9万元，相比于进口版Model3售价降幅显著。分析师认为Model3在动力性、经济性等各方面相比于国内主流车厂的竞品具有明显优势，在未来Model3零部件国产化程度进一步提升的情况下，其仍存在较大的降价空间，产品竞争力极强，有望在2020年逐步放量。</p><p>相关上市公司中，均胜电子（600699）子公司上海临港均胜汽车安全于近日收到特斯拉中国的定点意向函，正式确定临港均胜安全为特斯拉中国 Model 3 和 ModelY 车型的供应商。赣锋锂业（002460）向特斯拉供应电池级氢氧化锂产品，供应量为公司氢氧化锂产品当年总产能的20%。</p>
        </div>
        '''
        try:
            page = req.get(link).text
            doc = html.fromstring(page)
            article = doc.xpath("//div[@class='content']")[0].text_content()
        except:
            return None
        return article

    def get_list_json(self):
        items = []
        resp = req.get(self.page_url)
        if resp.status_code == 200:
            page = resp.text
            news_list = self._parse_list_page(page)
            if news_list:
                for news in news_list:
                    item = {}
                    current = news.get("morningNewsContent")
                    if current:
                        pub_date = news.get('morningNewsContent', {}).get("ctime")
                        title = news.get('morningNewsContent', {}).get("title")
                        article = news.get('morningNewsContent', {}).get("content")
                        aid = news.get('id')
                        link = 'https://api3.cls.cn/share/article/{}?os=web&sv=6.8.0&app=CailianpressWeb'.format(aid)
                        # print(pub_date)
                        # print(title)
                        # print(article)
                        # print(link)
                        item['title'] = title
                        item['pub_date'] = self.convert_dt(pub_date)
                        item['link'] = link
                        item['article'] = self._process_content(article)
                        items.append(item)
                    else:
                        pub_date = news.get("ctime")
                        title = news.get("title")
                        aid = news.get('id')
                        link = 'https://api3.cls.cn/share/article/{}?os=web&sv=6.8.0&app=CailianpressWeb'.format(aid)
                        item['title'] = title
                        item['pub_date'] = self.convert_dt(pub_date)
                        item['link'] = link
                        article = self._parse_app_page(link)
                        if article:
                            item['article'] = self._process_content(article)
                            items.append(item)
        return items

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS `cls_depth_theme`(
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime NOT NULL COMMENT '发布时间',
          `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `link` (`link`),
          KEY `pub_date` (`pub_date`)
        ) ENGINE=InnoDB AUTO_INCREMENT=34657 DEFAULT CHARSET=utf8mb4 COMMENT='财联社-深度及题材' ; 
        '''
        ret = self.sql_pool._exec_sql(create_sql)
        self.sql_pool.end()
        return ret

    def _start(self):
        self._init_pool()
        items = self.get_list_json()
        # print(items)
        # for item in items:
        #     print(item)
        self.save(items)


if __name__ == "__main__":
    # print(len('https://api3.cls.cn/share/article/441704?os=web&sv=6.8.0&app=CailianpressWeb'))
    demo = Reference(1)

    # demo._init_pool()
    # demo._create_table()

    demo._start()