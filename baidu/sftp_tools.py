# coding=utf-8
# 上传文件  https://juejin.im/post/5d80daa5e51d4562165535c0
import os
import paramiko

pravie_key_path = '/Users/furuiyang/.ssh/id_rsa'
key = paramiko.RSAKey.from_private_key_file(pravie_key_path)
# t = paramiko.Transport(('139.159.155.223', 9528))
t = paramiko.Transport(('139.9.193.142', 9528))
t.connect(username='furuiyang', pkey=key)
sftp = paramiko.SFTPClient.from_transport(t)
dir_path = "/Users/furuiyang/gitzip/JustSimpleSpider/baidu"

for file_name in os.listdir(dir_path):
    print(file_name)
    if os.path.isdir(file_name):
        pass
    else:
        source_file_path = os.path.join(dir_path, file_name)
        target_file_path = os.path.join("/home/furuiyang/baidu", file_name)
        sftp.put(source_file_path, target_file_path)
t.close()


# 下载 从服务器 sshd1 到本地
# rsync -e 'ssh -p 9528' -avz  furuiyang@139.159.155.223:/home/furuiyang/baidu/csv /Users/furuiyang/gitzip/JustSimpleSpider/baidu/load_csv/


# sshpp
# rsync -e 'ssh -p 9528' -avz  furuiyang@139.9.193.142:/home/furuiyang/baidu/csv /Users/furuiyang/gitzip/JustSimpleSpider/baidu/load_csv/
