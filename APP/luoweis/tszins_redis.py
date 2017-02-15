#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis
#redis 创建一个示例
#r = redis.StrictRedis(host='192.168.1.80',port=9736,db=0,password='P@ssword991120')
#创建redis链接池
#pool = redis.ConnectionPool(host='192.168.1.80',port=9736,db=0,password='P@ssword991120')
#r = redis.Redis(connection_pool=pool)
#r.get('name')

class tszins_redis():
    def __init__(self):
        self.host = '192.168.1.21'
        self.port = 9736
        self.db = 0
        self.password = 'P@ssword991120'
    #创建redis链接池
    def connection(self):
        pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db = self.db,
            password = self.password
        )
        r = redis.Redis(connection_pool=pool)
        return r
    def keyToRedisUseHset(self,bucket,key,value):
        r = self.connection()
        r.hset(bucket,key,value)
        return True
    def keyExistsInHset(self,bucket,key):
        r = self.connection()
        res = r.hexists(bucket,key)
        #res is bool type
        return res
    def keyDeleteFromHset(self,bucket,key):
        r = self.connection()
        r.hdel(bucket,key)

    def keyFromRedisUseHset(self,bucket):
        r = self.connection()
        res = r.hgetall(bucket)
        return res
    def bucketSize(self,bucket,size):
        r = self.connection()
        res = r.incrby(bucket+'_size',size)
        return res
    def test(self):
        r = self.connection()
        pass
