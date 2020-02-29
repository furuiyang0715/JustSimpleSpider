### 对整个舆情模块的部署
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/yuqing:v1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/yuqing:v1
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/yuqing:v1

sudo docker run --log-opt max-size=10m --log-opt max-file=3 -itd --name yuqing \
--env LOCAL=0 registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/yuqing:v1 
