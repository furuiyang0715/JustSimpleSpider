### 部署
```python
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao:v1 .
    
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao:v1

sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao:v1

sudo docker run -itd --name juchao registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao:v1

sudo docker logs -ft --tail 1000 juchao

```


### 相关信息 
表名： juchao_info
中文名：巨潮资讯
监控时间：9:30\16:00
SQL: SELECT count(id) FROM juchao_info WHERE pub_date > date_sub(CURDATE(), interval 1 day);
监控条数大于： 10
日期： 自然日