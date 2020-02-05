

def create_table_chinabank():
    """
    创建中国银行的数据表
    :return:
    """

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


def create_table_gov_stats():
    """
    创建国家统计局的数据表
    :return:
    """
    # 国家统计局 - 最新发布
    sql = """
    DROP TABLE IF EXISTS `gov_stats_zxfb`;

    CREATE TABLE `gov_stats_zxfb` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `pub_date` datetime not null  COMMENT '发布时间',
      `title` varchar(64) collate utf8_bin DEFAULT NULL COMMENT '文章标题',
      `link` varchar(128) collate utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
      `article` text collate utf8_bin DEFAULT NULL COMMENT '详情页内容',
      `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
      `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`), 
      KEY `pub_date` (`pub_date`)
    ) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COMMENT='国家统计局[最新发布]'; 

    ALTER TABLE `gov_stats_zxfb` ADD unique(`link`); 

    show full columns from gov_stats_zxfb;
    """

    # 国家统计局 - 新闻发布会
    sql = """
        DROP TABLE IF EXISTS `gov_stats_xwfbh`;

        CREATE TABLE `gov_stats_xwfbh` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `pub_date` datetime not null  COMMENT '发布时间',
          `title` varchar(64) collate utf8_bin DEFAULT NULL COMMENT '文章标题',
          `link` varchar(128) collate utf8_bin DEFAULT NULL COMMENT '文章详情页链接',
          `article` text collate utf8_bin DEFAULT NULL COMMENT '详情页内容',
          `CREATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP,
          `UPDATETIMEJZ` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`), 
          KEY `pub_date` (`pub_date`)
        ) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COMMENT='国家统计局[新闻发布会]'; 

        ALTER TABLE `gov_stats_xwfbh` ADD unique(`link`); 

        show full columns from gov_stats_xwfbh;
        """
