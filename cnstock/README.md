## 上海证券报爬虫 

###  主链接 
```python
http://www.cnstock.com/
```

### 分栏目

- 要闻：http://news.cnstock.com/
    - 宏观： http://news.cnstock.com/news/sns_yw/index.html
    - 金融： http://news.cnstock.com/news/sns_jg/index.html

- 产业：http://news.cnstock.com/industry
    - 上证4小时 http://news.cnstock.com/theme/index.html

- 公司：http://company.cnstock.com/
    - 公司聚焦：http://company.cnstock.com/company/scp_gsxw
    - 公告快讯：http://ggjd.cnstock.com/company/scp_ggjd/tjd_ggkx
    - 公告解读：http://ggjd.cnstock.com/company/scp_ggjd/tjd_bbdj

- 市场：http://stock.cnstock.com/
    - 直播： http://stock.cnstock.com/live
    - 新股：http://stock.cnstock.com/xg
    - 基金：http://stock.cnstock.com/jj.html
    - 券业：http://news.cnstock.com/news/sns_qy/index.html
    - 债券：http://stock.cnstock.com/zq.html
    - 信托：http://stock.cnstock.com/xt.html

- 科创板：http://news.cnstock.com/kcb 
    - 要闻：http://news.cnstock.com/kcb/skc_tt
    - 监管：http://news.cnstock.com/kcb/skc_jgfx
    - 公司：http://news.cnstock.com/kcb/skc_sbgsdt
    - 投资：http://news.cnstock.com/kcb/skc_tzzn
    - 观点：http://news.cnstock.com/kcb/skc_gd

- 新三板：http://jrz.cnstock.com/yw 
    - 要闻：http://jrz.cnstock.com/yw
    
### 部署
```python
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/cnstock:v1 .
    
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/cnstock:v1

sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/cnstock:v1

sudo docker run -itd --name cn_stock registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/cnstock:v1

sudo docker logs -ft --tail 1000 cn_stock
```

部署时更换 .conf 的配置即可。 

### 相关信息 
表名： cn_stock
中文名：上海证券报
监控时间：9:30\16:00
SQL: SELECT count(id) FROM cn_stock WHERE pub_date > date_sub(CURDATE(), interval 1 day);
监控条数大于： 10
日期： 自然日


