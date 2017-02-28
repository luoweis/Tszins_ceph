#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
#定义上传到web服务器端的目录位置
UPLOAD_FOLDER=os.path.abspath(os.curdir)+'/APP/upload'

#定义redis的参数
redis_server = '192.168.1.21'
redis_port = 9736
redis_db = 0
redis_password = 'P@ssword991120'
#定义ceph-radosgw的S3参数
ceph_access_key = 'SWBZYBGGJOMLWPXR4O15'
ceph_secret_key = 'XONMdWpLvAw2OpDHIjT0kqc0i1xj1KOqDKYuJExX'
ceph_radosgw_host = '192.168.1.40'
ceph_radosgw_port = 80
ceph_access_grantID = 'tszins'

#定义管理员的邮箱
adminsEmail = {
        'luoweis@126.com':u'施罗伟',
        'zhangsan@163.com':'zhangsan'
    }
#定义管理员的密码
admins = {
    'luoweis':{'username':u'施罗伟','password':'a44df41524d1b7198e6e2c3cda445caf','role':'super'},
    'luyan':{'username':u'路艳','password':'21c1d68ef134b83673c7e4dc85465401','role':'user'},#**123456
    'guoyingchen':{'username':u'郭颖琛','password':'8db497c587baf7f24b9ab5874cf4e26a','role':'user'}
}

#定义qcloud,腾讯云对象存储cos
qcloud_appid = 1252973300
qcloud_secret_id = u'AKIDsb9VfcrwISSIzUrwadb8Vl084JPMomCP'
qcloud_secret_key = u'EVdeU8ZorhLn5Xs12v79zzqV0IOuIZii'
qcloud_region_info = "tj"

#定义当前的ceph存储总量 单位GB
ceph_save_total=2232
ceph_save_total_KB = ceph_save_total*1024*1024*1024