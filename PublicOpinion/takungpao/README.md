大公网首页 > 大公财经 > 港股频道 >: http://finance.takungpao.com/hkstock/ 
    > 财经时事 >: http://finance.takungpao.com/hkstock/cjss/ 
    > 公司要闻 >: http://finance.takungpao.com/hkstock/gsyw/ 
    > 机构视点 >: http://finance.takungpao.com/hkstock/jgsd/ 
    > 全球股市 >: http://finance.takungpao.com/hkstock/qqgs/ 
    > 国际聚焦 >: http://finance.takungpao.com/hkstock/gjjj/ 
    > 经济一周 >: http://finance.takungpao.com/hkstock/jjyz/ 
    
大公网首页 > 大公财经 > 风口>: http://finance.takungpao.com/fk/ 
大公网首页 > 大公财经 > 旅游>: http://finance.takungpao.com/travel/ 

首页 > 财经 > 中国经济: http://www.takungpao.com/finance/236132/index.html 
首页 > 财经 > 香港财经: http://www.takungpao.com/finance/236131/index.html 
首页 > 财经 > 国际经济: http://www.takungpao.com/finance/236133/index.html
首页 > 财经 > 经济观察家: http://www.takungpao.com/finance/236134/index.html    # !!! 
首页 > 财经 > 港股: http://www.takungpao.com/finance/236135/index.html
首页 > 财经 > 地产: http://www.takungpao.com/finance/236136/index.html 
首页 > 财经 > 商业: http://www.takungpao.com/finance/236137/index.html 
首页 > 财经 > 新经济浪潮: http://www.takungpao.com/finance/236160/index.html 


建表： 
CREATE TABLE `takungpao` (
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
) ENGINE=InnoDB AUTO_INCREMENT=299 DEFAULT CHARSET=utf8mb4 COMMENT='大公报-财经类';
