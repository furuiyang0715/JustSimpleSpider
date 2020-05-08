## task 名称: 接续聚源的融资融券标的变更历史表 

### tower
复现聚源数据库融资融券标的证券 MT_TargetSecurities表单内容 ( https://tower.im/teams/12559/todos/37466 ) 

### 什么是融资融券标的证券 
#### 参考 
- https://baike.baidu.com/item/%E8%9E%8D%E8%B5%84%E8%9E%8D%E5%88%B8%E6%A0%87%E7%9A%84%E8%AF%81%E5%88%B8/12750327 
- https://www.zhihu.com/question/19941058 
- https://zhuanlan.zhihu.com/p/24609805?refer=taojinxiaobing 


### 聚源表说明
#### 表说明 
- 名称: 融资融券标的证券  
- 表名: MT_TargetSecurities
- 聚源链接: 
    - https://www.joinquant.com/help/data/data?name=jy#nodeId=112  
    - [已过期] https://dd.gildata.com/#/tableShow/942/column//all/MT_Target 

- 说明:   
    - 1.收录国内交易所公布的融资融券标的清单，包括融资买入标的和融券卖出标的；同时还收录了有披露起证券历次入选和剔除融资（融券）标的变化情况。
    - 2.历史数据：交易所披露数据最早记录可追溯至2006年8月
    - 3.数据来源：聚源按照上交所、深交所原始披露整理
    - 表数据更新频率： 不定时更新
#### 表字段 
- SecuMarket: 证券市场(SecuMarket)与(CT_SystemConst)表中的DM字段关联，令LB = 201 AND DM IN (83,90)，得到证券市场的具体描述：83-上海证券交易所，90-深圳证券交易所。 
- InnerCode: 证券内部编码（InnerCode）：与“证券主表（SecuMain）”中的“证券内部编码（InnerCode）”关联，得到标的证券的交易代码、简称等。 
- InDate: 调入日期 
- OutDate: 调出日期 
- TargetCategory: 标的类别(TargetCategory)与(CT_SystemConst)表中的DM字段关联，令LB = 1575 AND DM IN (10,20)，得到标的类别的具体描述：10-融资买入标的，20-融券卖出标的。 
- TargetFlag: 标的标志, 该字段固定以下常量（通过剔除日期判断）：1-是标的证券；0-不是标的证券。 
- ChangeReasonDesc: 变更原因描述 
- UpdateTime: 更新时间  

### 数据源
#### 上交所 
- http://www.sse.com.cn/services/tradingservice/margin/home/ 

#### 深交所 
- http://www.szse.cn/disclosure/margin/object/index.html 



### sql 
```shell script

# 查看证券市场的类型
select distinct(SecuMarket) from mt_targetsecurities ; 

# 查看标的类型 
select distinct(TargetCategory) from mt_targetsecurities ; 

# 查看标的状态 
select distinct(TargetFlag) from mt_targetsecurities ; 

# 查看变更原因描述 
select distinct(ChangeReasonDesc) from mt_targetsecurities ; 
# NULL 

# 查看聚源库最近的更新时间 
select max(UpdateTime) from mt_targetsecurities ; 
# 2020-04-20 09:04:01 

# 根据内部编码查看相关信息 
select * from secumain where InnerCode = 3\G 

```