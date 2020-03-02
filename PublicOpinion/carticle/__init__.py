# 东财-财富号

# 部署
# docker build -f Dockerfile.debug -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1 .
# docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1
# sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1
# sudo docker run -itd --name dongc --env LOCAL=0 registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/ca:v1

# 监控
# SELECT count(id) FROM  eastmoney_carticle  WHERE pub_date > date_sub(CURDATE(), interval 1 day);
# 监控触发阈值设置为 100

