### 部署
```python
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/qq_astock:v0.0.1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/qq_astock:v0.0.1


sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/qq_astock:v0.0.1
sudo /usr/local/bin/docker-compose up -d
sudo docker logs -ft --tail 1000 qq_astock
sudo docker image prune

use little_crawler
```