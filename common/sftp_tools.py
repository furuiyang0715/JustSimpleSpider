# coding=utf-8
import os
import paramiko


pravie_key_path = '/Users/furuiyang/.ssh/id_rsa'
key = paramiko.RSAKey.from_private_key_file(pravie_key_path)
# t = paramiko.Transport(('139.159.155.223', 9528))
t = paramiko.Transport(('139.9.193.142', 9528))
t.connect(username='furuiyang', pkey=key)
sftp = paramiko.SFTPClient.from_transport(t)
dir_path = "/Users/furuiyang/gitzip/JustSimpleSpider"

for file_name in os.listdir(dir_path):
    print(file_name)
    if os.path.isdir(file_name):
        pass
    else:
        source_file_path = os.path.join(dir_path, file_name)
        target_file_path = os.path.join("/home/furuiyang/JustSimpleSpider", file_name)
        sftp.put(source_file_path, target_file_path)
t.close()


# 下载 从服务器 sshd1 到本地
# rsync -e 'ssh -p 9528' -avz  furuiyang@139.159.155.223:/home/furuiyang/bbd/data_dir /Users/furuiyang/gitzip/JustSimpleSpider/bbd/remote_csv

# sshpp
# rsync -e 'ssh -p 9528' -avz  furuiyang@139.9.193.142:/home/furuiyang/bbd/sshpp_csv /Users/furuiyang/gitzip/JustSimpleSpider/bbd/remote_csv
# rsync -e 'ssh -p 9528' -avz  furuiyang@139.9.193.142:/home/furuiyang/JustSimpleSpider/ /Users/furuiyang/gitzip/JustSimpleSpider


'''
rsync -e 'ssh -p 9528' -avz  /Users/furuiyang/gitzip/JustSimpleSpider furuiyang@139.9.193.142:/home/furuiyang/ 


cd JustSimpleSpider 


sudo docker build -f Dockerfile -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spi:v1 .  


rm /home/furuiyang/JustSimpleSpider/SpidersSchedule/main.log
echo "" > /home/furuiyang/JustSimpleSpider/SpidersSchedule/main.log


sudo /home/furuiyang/spi/bin/python3 /home/furuiyang/JustSimpleSpider/SpidersSchedule/docker_main.py start 


tail -f /home/furuiyang/JustSimpleSpider/SpidersSchedule/main.log 




'''

