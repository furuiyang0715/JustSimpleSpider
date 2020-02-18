## 官媒

### 中国银行 
#### 任务详情 
Tower 任务: 中国人民银行资讯采集 ( https://tower.im/teams/12559/todos/29256 )
#### 建表并查看 
```shell script
CREATE TABLE IF NOT EXISTS `chinabank` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pubdate` datetime NOT NULL COMMENT '发布时间',
  `article_title` varchar(64) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章标题',
  `article_link` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
  `article_content` text CHARACTER SET utf8 COLLATE utf8_bin COMMENT '详情页内容',
  `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
  `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `article_link` (`article_link`),
  KEY `pubdate` (`pubdate`)
) ENGINE=InnoDB AUTO_INCREMENT=2383 DEFAULT CHARSET=utf8mb4 COMMENT='中国银行'; 

SHOW FULL COLUMNS FROM `chinabank`;
```
#### 分栏目 
中国银行包括数据解读以及新闻发布两个栏目，共用一张数据表。 
#### 部署信息

