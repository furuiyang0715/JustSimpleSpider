import datetime

import pymongo
import pandas as pd

file = '/Users/furuiyang/gitzip/JustSimpleSpider/my_stock/buy.txt'
df = pd.read_csv(file, encoding='utf-8')
datas = df.to_dict('records')


code_map = {
    "螺丝钉指数基金组合(CSI666)": 'CSI666',
    "华安德国30(DAX)ETF连接": '000614',
    "华安标普全球石油指数(160416)": "160416",
    "我要稳稳的幸福(CSI1014)": "CSI1014",
    "辣妈精选基金组合(CSI2009)": "CSI2009",
    "华夏恒生ETF联接": "000071",
    "钉钉宝365": "CSI1019",
    "钉钉宝90": "CSI1021",
    "天弘中证食品饮料指数C": "001632",
    "广发中证全指家用电器指数A": "005063",
    "招商央视50指数": "217027",
    "大成纳斯达克100指数": "000834",
    "嘉实全球互联网股票": "000988",
    "交银中证海外中国互联网指数": "164906",




}


mongo_client = pymongo.MongoClient("127.0.0.1:27017")
fund_cli = mongo_client.myfund.records
for data in datas:
    print(data)
    item = dict()
    item['time'] = datetime.datetime.strptime(data.get("时间"), "%Y/%m/%d")
    item['direction'] = 1 if data.get("方向") == "买入" else 2
    item['amount'] = float(data.get("金额"))
    item['fund_name'] = data.get("类别")
    item['code'] = code_map.get(data.get("类别"))
    item['app'] = "蛋卷基金"





# demo = {"time": "", "name": "", "direction": "buy", "amount": "", "code": "", "app": ""}