## 官媒

### 中国银行 
#### 任务详情 
Tower 任务: 中国人民银行资讯采集 ( https://tower.im/teams/12559/todos/29256 )
#### 建表并查看 
```shell script
CREATE TABLE IF NOT EXISTS `chinabank` (
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
) ENGINE=InnoDB AUTO_INCREMENT=2383 DEFAULT CHARSET=utf8mb4 COMMENT='中国银行'; 

SHOW FULL COLUMNS FROM `chinabank`;
```
#### 分栏目 
中国银行包括[数据解读]以及[新闻发布]两个栏目，共用一张数据表。 
#### 部署信息

### 国家统计局
#### 任务详情
Tower 任务: 国家统计局资讯采集 ( https://tower.im/teams/12559/todos/29254 )
#### 建表并查看 
```shell script
CREATE TABLE `gov_stats` (
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
) ENGINE=InnoDB AUTO_INCREMENT=299 DEFAULT CHARSET=utf8mb4 COMMENT='国家统计局';
```
#### 分栏目 
国家统计局包括[最新发布][数据解读][统计动态][新闻发布会]四个栏目, 共用一张数据表。 
#### 部署信息 

docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/gover:v0.0.1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/gover:v0.0.1


sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/gover:v0.0.1

// 首次部署
sudo docker run -itd --name gov registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/gover:v0.0.1
// 增量部署
sudo docker run -itd --name gov --env FIRST=0 registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/gover:v0.0.1

sudo docker logs -ft --tail 1000 gov
sudo docker image prune
