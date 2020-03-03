|  名称  | 文件  |  链接 | 
|  ----  | ----  | ---- | 
| 巨丰内参 | reference.py | http://www.jfinfo.com/reference | 
| 巨丰港股资讯  | hk_info.py | http://www.jfinfo.com/reference/HK | 
| 巨丰投资者教育 | tzzjy.py | http://www.jfinfo.com/reference/tzzjy | 
| 巨丰研究院 | research.py | http://www.jfinfo.com/research | 

### 建表 
CREATE TABLE `jfinfo` (
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
) ENGINE=InnoDB AUTO_INCREMENT=299 DEFAULT CHARSET=utf8mb4 COMMENT='巨丰财经';
