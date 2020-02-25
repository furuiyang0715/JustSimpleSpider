def parse_list_first(doc):
    '''
<dl class="hotNews">
    <dt>
        <a href="http://kcb.stcn.com/2020/0225/15680344.shtml" target="_blank" title="包容性强 科创板成TMT企业IPO上市首选"><img src="http://upload.stcn.com/2019/0506/1557126325788.jpg"></a>
    </dt>
    <dd class="tit">
        <a href="http://kcb.stcn.com/2020/0225/15680344.shtml" target="_blank" title="包容性强 科创板成TMT企业IPO上市首选">包容性强 科创板成TMT企业IPO上市首选</a>
    </dd>
    <dd class="exp">
        近日，普华永道发布的《2019年下半年中国科技媒体通信行业（TMT）IPO回顾与前瞻》（下称报告，TMT代指科技、媒体及通讯行业）显示，科创板的设立以及注册制的试点为科创类企业创造了良好的市场环境。            </dd>
    <dd class="sj">2020-02-25<span>07:56</span></dd>
</dl>
    '''
    first = doc.xpath("//dl[@class='hotNews']")[0]
    title = first.xpath("//dt/a/@title")[0]
    link = first.xpath("//dt/a/@href")[0]
    pub_date = first.xpath("//dd[@class='sj']")[0].text_content()
    pub_date = '{} {}'.format(pub_date[:10], pub_date[10:])
    first = dict()
    first['title'] = title
    first['link'] = link
    first['pub_date'] = pub_date
    return first
