#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#定义上传到web服务器端的目录位置
UPLOAD_FOLDER='/Users/luoweis/tszins'
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
        'luoweis@126.com':'luoweis',
        'zhangsan@163.com':'zhangsan'
    }
#定义管理员的密码
admins = {
    'luoweis':'a44df41524d1b7198e6e2c3cda445caf',
    'test':'a44df41524d1b7198e6e2c3cda445caf',
    'luyan':'21c1d68ef134b83673c7e4dc85465401'#**123456

}
#定义qcloud,腾讯云对象存储cos
qcloud_appid = 1252973300
qcloud_secret_id = u'AKIDsb9VfcrwISSIzUrwadb8Vl084JPMomCP'
qcloud_secret_key = u'EVdeU8ZorhLn5Xs12v79zzqV0IOuIZii'
qcloud_region_info = "tj"

