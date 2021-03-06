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
import os,math,json,sys
from filechunkio import FileChunkIO
import tszins_redis
import config
reload(sys)
sys.setdefaultencoding('utf-8')

class object_storage(object):
    def __init__(self):
        self.access_key = config.ceph_access_key
        self.secret_key = config.ceph_secret_key
        self.host = config.ceph_radosgw_host
        self.port = config.ceph_radosgw_port
        self.is_secure = False
        self.grantID = config.ceph_access_grantID
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
        totalSize = 0
        red = tszins_redis.tszins_redis()
        r = red.connection()
        for bucket in buckets:
            bucketInfo={}
            c=0
            for key in bucket.list():
                c+=1
            cc+=c
            bucketInfo['name'] = bucket.name
            bucketInfo['create'] = bucket.creation_date
            bucketInfo['count'] = c
            size = r.get(bucket.name+'_size') or 0#size type is str
            bucketInfo['size'] = size
            size = int(size)#chang str to int
            totalSize+=size
            bucketlist.append(bucketInfo)
        bucketsInfo['buckets'] = bucketlist
        bucketsInfo['keys'] = cc
        bucketsInfo['totalSize'] = totalSize#所有key的size总量
        return bucketsInfo

    #创建一个bucket
    def bucketCreate(self,bucket):
        conn = self.connection()
        conn.create_bucket(bucket)
    #删除一个为空的bucket
    def bucketDel(self,bucket):
        conn = self.connection()
        conn.delete_bucket(bucket)

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
        return True
    #小文件
    def keyCreateSmall(self,bucket,filename,source_path,**kwargs):
        conn = self.connection()
        b = conn.get_bucket(bucket)
        k = Key(b)
        k.key = filename
        k.set_contents_from_filename(source_path)
        return True

    #创建一个文件夹
    '''
    对于对象存储而言，没有文件夹的概念，所有的文件以及文件夹都看成是一个object，但是object前面可以有字符“/”来表示文件夹意义的标示符，
    因而本身s3是没有提供直接建文件夹的API的，但是利用前面的概念可以建一个结尾带有“/”的key，这个key的content为空，来象征性的标示文件夹
    '''
    def createFloder(self,bucket,name,prefix='',**kwargs):
        conn = self.connection()
        b = conn.get_bucket(bucket)
        k = Key(b)
        k.key = prefix+name+'/'
        k.set_contents_from_string('')
        return True
    #列出某个bucket中的所有的key的方法
    def keysList(self,bucketName):
        conn = self.connection()
        bucket = conn.get_bucket(bucketName)
        keys = bucket.list()
        d = {}
        L = []
        red = tszins_redis.tszins_redis()
        r = red.connection()
        for key in keys:
                acls = self.getKeyAcl(bucketName,key)#获得key的权限
                value = r.hget(bucketName,key.name)#从redis中取得的结果是 str类型，value 的类型是str 需要json转换
                value = eval(value)#通过eval方法将str 转换成字典
                tag = value['tag']
                try:
                    group = value['group']
                except:
                    group = ''

                if acls.has_key('others'):
                    d[key.name] = {'size':key.size,'date':key.last_modified,'acl':acls['others'],'tag':tag,'group':group}
                else:
                    d[key.name] = {'size': key.size, 'date': key.last_modified, 'acl': 'private','tag':tag,'group':group}
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
        #bucket.set_acl('public-read')
        bucket.set_acl('private')
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
                KeyUrl = k.generate_url(86400, query_auth=True, force_http=True)
            elif kwargs['FULL_CONTROL']:
                KeyUrl = k.generate_url(86400, query_auth=True, force_http=True)
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
            if grant.id == self.grantID:
                acls['owner'] = grant.permission
            else:
                if not grant.permission:
                    acl['others'] = 'private'
                else:
                    acls['others'] = grant.permission
        return acls
    #获取bucket的权限
    def getBucketAcl(self,bucket):
        conn=self.connection()
        b = conn.get_bucket(bucket)
        acl = b.get_acl().acl.grants
        return acl

    #删除指定bucket中的指定的key
    def deleteKey(self,bucket,key):
        conn=self.connection()
        b=conn.get_bucket(bucket)
        b.delete_key(key)

