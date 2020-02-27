FROM registry.cn-shenzhen.aliyuncs.com/jzdev/tinibase:1.0.0

ENV TZ=Asia/Shanghai

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir /PublicOpinion

WORKDIR /PublicOpinion

ADD . /PublicOpinion

WORKDIR /PublicOpinion

RUN pip install -r requirements.txt -i https://pypi.douban.com/simple

WORKDIR /PublicOpinion/carticle

#ENTRYPOINT ["python", "myarticle.py"]
ENTRYPOINT ["python", "main.py"]
