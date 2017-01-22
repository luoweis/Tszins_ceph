#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
作者：luoweis
日期：2017-1-16
处理对象存储的一个类
需要提前创建s3 user
1 定义链接对象存储集群的方法：conn()
2 定义列出所有buckets的方法：bucketsList()
3 定义创建bucket的方法：bucketCreate()
4 定义列出某个bucket下的所有key的方法: keysList()
5 定义创建在某个bucket下的key: keyCreate()
'''
import boto
import boto.s3.connection
from boto.s3.key import  Key
import os,math
from filechunkio import FileChunkIO

class object_storage(object):
    def __init__(self):
        self.access_key = 'A4C11AG3OXAAA13ACB7Z'
        self.secret_key = 'n51WBWfEB6R0JAUtfsDWC3uP6WHSvzwCq5BKbFOU'
        self.host = '192.168.1.70'
        self.port = 80
        self.is_secure = False
    #创建链接
    def connection(self):
        conn = boto.connect_s3(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            host=self.host,
            port=self.port,
            is_secure=self.is_secure,
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
        )
        return conn

    #列出所有的bucket
    def bucketsList(self):
        conn= self.connection()
        buckets = conn.get_all_buckets()
        bucketsInfo={}
        bucketlist=[]
        bucketsInfo['count'] = len(buckets)
        cc = 0
        for bucket in buckets:
            bucketInfo={}
            c=0
            for key in bucket.list():
                c+=1
            cc+=c
            bucketInfo['name'] = bucket.name
            bucketInfo['create'] = bucket.creation_date
            bucketInfo['count'] = c
            bucketlist.append(bucketInfo)
        bucketsInfo['buckets'] = bucketlist
        bucketsInfo['keys'] = cc
        return bucketsInfo

    #创建一个bucket的函数
    def bucketCreate(self,CreateBucketName):
        conn = self.connection()
        conn.create_bucket(CreateBucketName)
    #创建bucket中的对象的方法
    #大于50M的文件
    def keyCreate(self,bucket,source_path,source_size,**kwargs):
        conn = self.connection()
        b = conn.get_bucket(bucket)
        mp = b.initiate_multipart_upload(os.path.basename(source_path))
        chunk_size = 52428800 #50MiB
        chunk_count = int(math.ceil(source_size/float(chunk_size)))
        for i in range(chunk_count):
            offset = chunk_size * i
            bytes = min(chunk_size,source_size - offset)
            with FileChunkIO(source_path,'r',offset=offset,bytes=bytes) as fp:
                mp.upload_part_from_file(fp,part_num=i + 1)
        mp.complete_upload()
    #小文件
    def keyCreateSmall(self,bucket,filename,source_path,**kwargs):
        conn = self.connection()
        b = conn.get_bucket(bucket)
        k = Key(b)
        k.key = filename
        k.set_contents_from_filename(source_path)

    #列出某个bucket中的所有的key的方法
    def keysList(self,bucketName):
        conn = self.connection()
        bucket = conn.get_bucket(bucketName)
        keys = bucket.list()
        d = {}
        L = []
        for key in keys:
            acls = self.getKeyAcl(bucketName,key)#获得key的权限
            if acls.has_key('others'):
                d[key.name] = {'size':key.size,'date':key.last_modified,'acl':acls['others']}
            else:
                d[key.name] = {'size': key.size, 'date': key.last_modified, 'acl': 'private'}
            L.append(d)
            d={}
        return L

    #下载指定的bucket下的某个key到ceph-obj服务器本地
    def keyDownload(self,bucketName,keyName):
        conn = self.connection()
        bucket = conn.get_bucket(bucketName)
        #判断是否有指定的key存在
        k = bucket.get_key(keyName)
        if k:
            key = bucket.lookup(keyName)
            key.get_contents_to_filename(keyName)
    #修改key的ACL
    '''
    有四种授权模式
    private：所有者有full权限，其他人没有任何权限
    public-read：所有者有full权限，匿名用户有读的权限
    public-write：所有者有full权限，匿名用户有读写的权限
    authenticated-read:所有者有full权限，所有S3注册过的用户有读权限
    '''
    def acl_create(self,bucketName,keyName,**kwargs):
        conn = self.connection()
        bucket = conn.get_bucket(bucketName)
        bucket.set_acl('public-read')
        # 判断是否有指定的key存在
        k = bucket.get_key(keyName)
        if k:
            if kwargs.has_key('acl'):
                bucket.set_acl(kwargs['acl'],keyName)

    #提取某个bucket下的key的URL 为read权限准备
    def GetKeyUrl(self,bucketName,keyName,**kwargs):
        conn = self.connection()
        bucket = conn.get_bucket(bucketName)
        KeyUrl=''
        # 判断是否有指定的key存在
        k = bucket.get_key(keyName)
        if k:
            if kwargs['private'] == True:
                KeyUrl = k.generate_url(3600, query_auth=True, force_http=True)
            else:
                KeyUrl=k.generate_url(0, query_auth=False, force_http=True)
        return KeyUrl

    #获取一个key的权限
    def getKeyAcl(self,bucket,key):
        conn=self.connection()
        b = conn.get_bucket(bucket)
        k = b.lookup(key)
        acp = k.get_acl()
        acl = acp.acl.grants
        acls = {}
        for grant in acl:
            #print grant.permission,grant.display_name, grant.email_address, grant.id
            if grant.id == 'luoweis':
                acls['owner'] = grant.permission
            else:
                if not grant.permission:
                    acl['others'] = 'private'
                else:
                    acls['others'] = grant.permission
        return acls
    #删除指定bucket中的指定的key
    def deleteKey(self,bucket,key):
        conn=self.connection()
        b=conn.get_bucket(bucket)
        b.delete_key(key)
