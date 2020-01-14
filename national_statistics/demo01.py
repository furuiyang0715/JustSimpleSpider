
# 测试获取列表页面
import requests as req
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import DesiredCapabilities

from selenium.webdriver.support import expected_conditions as EC

# browser = webdriver.Chrome()
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"  # 懒加载模式，不等待页面加载完毕
browser = webdriver.Chrome(desired_capabilities=capa)  # 关键!记得添加
wait = WebDriverWait(browser, 20)  # 等待的最大时间20s



browser.get("http://www.stats.gov.cn/tjsj/zxfb/")
ret = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='center_list']/ul[@class='center_list_contlist']")))   # 等待直到某个元素出现

print(ret.tag_name)  # ul
lines = ret.find_elements_by_xpath("./li/a/*")
for line in lines: 
    item = {}
    item['link'] = line.find_element_by_xpath("./..").get_attribute("href")
    item['title'] = line.find_element_by_xpath("./font[@class='cont_tit03']").text
    item['pub_date'] = line.find_element_by_xpath("./font[@class='cont_tit02']").text

    print(item)
    
browser.close()


"""
<ul class="center_list_contlist" style="min-height:350px;">
    <li>
        <a href="/tjsj/sjjd/202001/t20200109_1721987.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">解读：2019年12月份CPI涨幅稳定 PPI降幅收窄</font><font class="cont_tit02">2020-01-09</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./202001/t20200109_1721984.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">2019年12月份居民消费价格同比上涨4.5%</font><font class="cont_tit02">2020-01-09</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./202001/t20200109_1721985.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">2019年12月份工业生产者出厂价格同比下降0.5%</font><font class="cont_tit02">2020-01-09</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./202001/t20200106_1721413.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">2019年12月下旬流通领域重要生产资料市场价格变动情况</font><font class="cont_tit02">2020-01-06</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="/tjsj/sjjd/201912/t20191231_1720659.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">解读：2019年12月制造业采购经理指数稳定扩张 非制造业商务活动指数继续扩张</font><font class="cont_tit02">2019-12-31</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./201912/t20191231_1720657.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">2019年12月中国采购经理指数运行情况</font><font class="cont_tit02">2019-12-31</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="/tjsj/sjjd/201912/t20191227_1720023.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">国家统计局有关负责人就地区生产总值统一核算改革有关问题答记者问</font><font class="cont_tit02">2019-12-27</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="/tjsj/sjjd/201912/t20191227_1720053.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">解读：11月份工业利润同比增长5.4%</font><font class="cont_tit02">2019-12-27</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./201912/t20191227_1720052.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">2019年1—11月份全国规模以上工业企业利润下降2.1%</font><font class="cont_tit02">2019-12-27</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./201912/t20191224_1719270.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">2019年12月中旬流通领域重要生产资料市场价格变动情况</font><font class="cont_tit02">2019-12-24</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./201912/t20191220_1718680.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">小微商贸企业快速增长——第四次全国经济普查系列报告之十四</font><font class="cont_tit02">2019-12-20</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./201912/t20191219_1718494.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">批发和零售业、住宿和餐饮业就业规模持续扩大——第四次全国经济普查系列报告之十三</font><font class="cont_tit02">2019-12-19</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./201912/t20191218_1718313.html" target="_blank">

        <span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;">

        <font class="cont_tit03">中小微企业成为推动经济发展的重要力量——第四次全国经济普查系列报告之十二</font>
        <font class="cont_tit02">2019-12-18</font>

        </span>

        </a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./201912/t20191217_1718059.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">全国建筑业企业经营效益不断提升——第四次全国经济普查系列报告之十一</font><font class="cont_tit02">2019-12-17</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="/tjsj/sjjd/201912/t20191217_1718008.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">解读：2019年全国棉花产量小幅下降</font><font class="cont_tit02">2019-12-17</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./201912/t20191217_1718007.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">国家统计局关于2019年棉花产量的公告</font><font class="cont_tit02">2019-12-17</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="./201912/t20191213_1717470.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">全国建筑业企业生产规模快速扩大——第四次全国经济普查系列报告之十</font><font class="cont_tit02">2019-12-16</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="/tjsj/sjjd/201912/t20191216_1717808.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">解读：工业生产明显加快</font><font class="cont_tit02">2019-12-16</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="/tjsj/sjjd/201912/t20191216_1717809.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">解读：固定资产投资平稳增长 短板领域投资不断发力</font><font class="cont_tit02">2019-12-16</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    <li>
        <a href="/tjsj/sjjd/201912/t20191216_1717810.html" target="_blank"><span class="cont_tit"><img src="../../images/01.jpg" style="float:left;margin-right:5px;margin-top:5px;"><font class="cont_tit03">解读：社会消费品零售总额增长加快</font><font class="cont_tit02">2019-12-16</font></span></a>
    </li>
    <li class="cont_line" style=":&quot;background:" url(xx_li5.jpg)="" no-repeat="" left="" center;"="">&nbsp;</li>

    
    
    <li>
        <dl class="fenye">
        <!-- <dl class="xxgkml_fenye"> -->
共25页&nbsp;&nbsp;<span id="pagenav_0" style="color:#FF0000;padding-left:7px;padding-right:7px;">1</span><a id="pagenav_1" class="bai12_22h" style="padding-left:7px;padding-right:7px;" target="_self" href="index_1.html">2</a><a id="pagenav_2" class="bai12_22h" style="padding-left:7px;padding-right:7px;" target="_self" href="index_2.html">3</a><a id="pagenav_3" class="bai12_22h" style="padding-left:7px;padding-right:7px;" target="_self" href="index_3.html">4</a><a id="pagenav_4" class="bai12_22h" style="padding-left:7px;padding-right:7px;" target="_self" href="index_4.html">5</a><a id="pagenav_1" class="bai12_22h" style="padding-left:7px;padding-right:7px;" target="_self" href="index_1.html">下一页</a><a id="pagenav_nextgroup" class="bai12_22h" style="padding-left:7px;padding-right:7px;" target="_self" href="index_9.html">下5页</a><a id="pagenav_tail" class="bai12_22h" style="padding-left:7px;padding-right:7px;" target="_self" href="index_24.html">尾页</a> 	

        <font color="#2B73BB">更多信息请用<a href="http://www.stats.gov.cn/was5/web/adv.jsp" target="_blank">检索</a>查询</font></dl>
    </li>
</ul>
"""


# print(ret)
# print(dir(ret))
"""
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', 
'__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', 
'__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', 
'__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_execute', '_id', '_parent', 
'_upload', '_w3c', 

'clear', 'click', 'find_element', 'find_element_by_class_name', 
'find_element_by_css_selector', 'find_element_by_id', 'find_element_by_link_text', 
'find_element_by_name', 'find_element_by_partial_link_text', 'find_element_by_tag_name', 
'find_element_by_xpath', 'find_elements', 'find_elements_by_class_name', 
'find_elements_by_css_selector', 'find_elements_by_id', 'find_elements_by_link_text', 
'find_elements_by_name', 'find_elements_by_partial_link_text', 'find_elements_by_tag_name', 
'find_elements_by_xpath', 'get_attribute', 'get_property', 'id', 'is_displayed', 'is_enabled', 
'is_selected', 'location', 'location_once_scrolled_into_view', 'parent', 'rect', 'screenshot', 
'screenshot_as_base64', 'screenshot_as_png', 'send_keys', 'size', 'submit', 'tag_name', 
'text', 'value_of_css_property']

"""




