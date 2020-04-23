import pymongo
import pandas as pd

file = '/Users/furuiyang/gitzip/JustSimpleSpider/my_stock/buy.txt'
data = pd.read_csv(file, encoding='utf-8')
# print(data)
print(data.to_dict('records'))
# print(data.to_json())


mongo_client = pymongo.MongoClient("127.0.0.1:27017")
print(mongo_client)
fund_cli = mongo_client.myfund.records



# demo = {"time": "", "name": "", "direction": "buy", "amount": "", "code": "", "app": ""}