

def create_table():
    sql = """
    DROP TABLE IF EXISTS `chinabank_shujujiedu`;
    CREATE TABLE `chinabank_shujujiedu` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `pubdate` datetime not null  COMMENT '发布时间',
      `article_title` varchar(64) collate utf8_bin DEFAULT NULL COMMENT '文章标题',
      `article_link` varchar(128) collate utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
      `article_content` text collate utf8_bin DEFAULT NULL COMMENT '详情页内容',
      `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
      `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`), 
      KEY `pubdate` (`pubdate`)
    ) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COMMENT='中国银行[数据解读]'; 

    ALTER TABLE `chinabank_shujujiedu` ADD unique(`article_link`); 

    show full columns from chinabank_shujujiedu;
    """

    """
    DROP TABLE IF EXISTS `chinabank_xinwenfabu`;
    CREATE TABLE `chinabank_xinwenfabu` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `pubdate` datetime not null  COMMENT '发布时间',
      `article_title` varchar(64) collate utf8_bin DEFAULT NULL COMMENT '文章标题',
      `article_link` varchar(128) collate utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
      `article_content` text collate utf8_bin DEFAULT NULL COMMENT '详情页内容',
      `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
      `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`), 
      KEY `pubdate` (`pubdate`)
    ) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COMMENT='中国银行[新闻发布]'; 

    ALTER TABLE `chinabank_xinwenfabu` ADD unique(`article_link`); 

    """
