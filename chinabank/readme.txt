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

local.env 示例
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
（1） 按照 docker 部署的步骤打包镜像
（2） 启动爬虫服务的镜像以及依赖的浏览器驱动镜像 docker-compose up -d
      环境变量已经写在 compose 文件中的 environment 中

docker-compose.yml 示例

    version: "2.0"
    services:
      spider:
        image: registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1
        environment:
          MYSQL_HOST: 127.0.0.1
          MYSQL_PORT: 3306
          MYSQL_USER: root
          MYSQL_PASSWORD: nishizhu
          MYSQL_DB: test_furuiyang
          MYSQL_TABLE: chinabank_xinwenfabu
        depends_on:
          - chrome
      chrome:
        image: selenium/standalone-chrome:latest
        ports:
          - "4444:4444"
        shm_size: 2g

