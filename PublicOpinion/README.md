### 证券时报
#### 建表 
```shell script
CREATE TABLE `stcn_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pub_date` datetime NOT NULL COMMENT '发布时间',
  `code` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '股票代码',
  `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
  `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
  `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
  `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
  `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `link` (`link`),
  KEY `pub_date` (`pub_date`)
) ENGINE=InnoDB AUTO_INCREMENT=34657 DEFAULT CHARSET=utf8mb4 COMMENT='证券时报' ; 
```

### 淘股吧 
#### 建表
```shell script
CREATE TABLE `eastmoney_carticle` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pub_date` datetime NOT NULL COMMENT '发布时间',
  `code` varchar(16) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '股票代码',
  `title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
  `link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
  `article` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
  `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
  `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `link` (`link`),
  KEY `pub_date` (`pub_date`)
) ENGINE=InnoDB AUTO_INCREMENT=34657 DEFAULT CHARSET=utf8mb4 COMMENT='东财-财富号文章' ; 

```
#### 部署 
```shell script
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1 .
    
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1

sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1

# 拉取历史数据
sudo docker run -itd --name ins4 --env KEY='' --env START=600 \
--env END=1000 \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1 

### --------------------------------------------------------------------


docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/yuqing:v1 .
    
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/yuqing:v1

sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/yuqing:v1

sudo docker run --log-opt max-size=10m --log-opt max-file=3 -itd --name yuqing \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/yuqing:v1 

```
