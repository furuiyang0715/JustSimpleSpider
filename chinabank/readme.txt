### 使用单纯的 docker 部署

[local]
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1 .

docker run -itd --name ck --env-file local.env registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1

docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1

[test]
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1

sudo docker run -itd --name ck_shuju_test --env-file pp.env registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1
sudo docker run -itd --name ck_xinwen_test --env-file pp.env registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1


[pro]
sudo docker run -itd --name ck_shuju_pro --env-file pro.env registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1
sudo docker run -itd --name ck_xinwen_pro --env-file pro.env registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1

local.env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_USER=root
MYSQL_PASSWORD=ruiyang
MYSQL_DB=test_furuiyang
SELENIUM_HOST=172.17.0.6
#MYSQL_TABLE=chinabank_shujujiedu
#ALL_PAGES=23
MYSQL_TABLE=chinabank_xinwenfabu
ALL_PAGES=260

### 基于 docker-compose 部署
