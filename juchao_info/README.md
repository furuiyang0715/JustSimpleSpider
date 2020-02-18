### 部署
```python
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao:v1 .
    
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao:v1

sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao:v1

sudo docker run -itd --name juchao registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/juchao:v1

sudo docker logs -ft --tail 1000 juchao

```