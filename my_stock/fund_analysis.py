import pymongo

mongo_client = pymongo.MongoClient("127.0.0.1:27017")
cli = mongo_client.myfund.records

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
    "博时标普500ETF联接": "050025",
    "招商中证白酒指数": "161725",
    "广发中证环保ETF联接A": "001064",

}

# 计算投入总额
amounts = cli.find({}, {"_id": 0, "amount": 1})
amounts = [info.get("amount") for info in amounts]
# print(amounts)
print("买入总额: ",  sum(amounts))

# 计算各个基金买入量
for name, code in code_map.items():
    amounts = [info.get("amount") for info in cli.find({"code": code}, {"_id": 0, "amount": 1})]
    print("{} 合计买入 {} 元".format(name, sum(amounts)))
