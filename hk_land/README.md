## 陆股通实时数据 
### 所在文件 
lgt_s_n_money_data.py 
### 原始数据接口
http://push2.eastmoney.com/api/qt/kamt.rtmin/get?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55,f56&ut=b2884a393a59ad64002292a3e90d46a5&cb=jQuery18306854619522421488_1566280636697&_=1566284477196
### 爬虫数据表
lgt_south_money_data 陆股通-北向数据-东财 
lgt_north_money_data 陆股通-南向数据-东财
### 爬虫字段释义
Date: 日期, Datetime 格式; 
SHFlow: hk>>sh 当日资金流向(单位: 万)
SHBalance: hk>>sh 当日资金余额(单位: 万)
SZFlow: hk>>sz 当日资金流向(单位: 万)
SZBalance: hk>>sz 当日资金余额(单位: 万)
NorthMoney: hk>>north 北向资金总额(单位:万), 是 SHFlow 与 SZFlow 的总和
Category: 北向资金


同理: 
Date: 日期 
HKHFlow: sh>>hk 当日资金流向 
HKHBalance：sh>>hk 当日资金余额  
HKZFlow: sz>>hk 当日资金流向 
HKZBalance: sz>>hk 当日资金余额 
SouthMoney: sh+sz >> hk 南向资金总额(单位: 万), 是 HKHFlow 与 HKZFlow 的总和

### 爬虫表建表语句
CREATE TABLE IF NOT EXISTS `{}` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `Date` datetime NOT NULL COMMENT '日期',
  `SHFlow` decimal(19,4) DEFAULT NULL COMMENT '沪股通当日资金流向(万）',
  `SHBalance` decimal(19,4) DEFAULT NULL COMMENT '沪股通当日资金余额（万）',
  `SZFlow` decimal(19,4) DEFAULT NULL COMMENT '深股通当日资金流向(万）',
  `SZBalance` decimal(19,4) DEFAULT NULL COMMENT '深股通当日资金余额（万）',
  `NorthMoney` decimal(19,4) DEFAULT NULL COMMENT '北向资金',
  `Category` varchar(20) COLLATE utf8_bin DEFAULT NULL COMMENT '类别',
  `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
  `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_key` (`Date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='陆股通-北向资金-东财'; 

同理: 
CREATE TABLE IF NOT EXISTS `{}` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `Date` datetime NOT NULL COMMENT '日期',
  `HKHFlow` decimal(19,4) DEFAULT NULL COMMENT '港股通（沪）当日资金流向(万）',
  `HKHBalance` decimal(19,4) DEFAULT NULL COMMENT '港股通（沪）当日资金余额（万）',
  `HKZFlow` decimal(19,4) DEFAULT NULL COMMENT '港股通（深）当日资金流向(万）',
  `HKZBalance` decimal(19,4) DEFAULT NULL COMMENT '港股通（深）当日资金余额（万）',
  `SouthMoney` decimal(19,4) DEFAULT NULL COMMENT '南向资金',
  `Category` varchar(20) COLLATE utf8_bin DEFAULT NULL COMMENT '类别',
  `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
  `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_key` (`Date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='陆股通-南向资金-东财'; 

### 正式数据库 
hkland_flow 

### 正式表字段释义 
DateTime: 交易时间 datetime 类型，对应于爬虫库中的日期 
ShHkFlow: 如果 Category=1, 为 sh>>hk 当日资金流向; Category=2, 为 hk>>sh 当日资金流向 
ShHkBalance: 如果 Category=1, 为 sh>>hk 当日资金余额; Category=2, 为 hk>>sh 当日资金余额
SzHkFlow: 如果 Category=1, 为 sz>>hk 当日资金流向; Category=2, 为 hk>>sz 当日资金流向  
SzHkBalance: 如果 Category=1, 为 sz>>hk 当日资金余额; Category=2, 为 hk>>sz 当日资金余额 
Netinflow: 如果 Category=1, 为 sh>>hk + sz>>hk 总额; Category=2, 为 hk>>sh + hk>>sz 总额
Category: 类别:1 南向, 2 北向


### 正式表建表语句 
CREATE TABLE IF NOT EXISTS `{}` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `DateTime` datetime NOT NULL COMMENT '交易时间',
  `ShHkFlow` decimal(19,4) NOT NULL COMMENT '沪股通/港股通(沪)当日资金流向(万）',
  `ShHkBalance` decimal(19,4) NOT NULL COMMENT '沪股通/港股通(沪)当日资金余额（万）',
  `SzHkFlow` decimal(19,4) NOT NULL COMMENT '深股通/港股通(深)当日资金流向(万）',
  `SzHkBalance` decimal(19,4) NOT NULL COMMENT '深股通/港股通(深)当日资金余额（万）',
  `Netinflow` decimal(19,4) NOT NULL COMMENT '南北向资金,当日净流入',
  `Category` tinyint(4) NOT NULL COMMENT '类别:1 南向, 2 北向',
  `HashID` varchar(50) COLLATE utf8_bin DEFAULT NULL COMMENT '哈希ID',
  `CMFID` bigint(20) unsigned DEFAULT NULL COMMENT '源表来源ID',
  `CMFTime` datetime DEFAULT NULL COMMENT 'Come From Time',
  `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
  `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_key2` (`DateTime`,`Category`),
  UNIQUE KEY `unique_key` (`CMFID`,`Category`),
  KEY `DateTime` (`DateTime`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='陆港通-实时资金流向';


