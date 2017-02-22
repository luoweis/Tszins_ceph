#!/usr/bin/env python
# -*- coding: utf-8 -*-
from APP import app
import qcloud_cos
from qcloud_cos import cos_request
import config
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class qcloud_tszins():
    def __init__(self):
        self.appid = config.qcloud_appid
        self.secret_id = config.qcloud_secret_id
        self.secret_key = config.qcloud_secret_key
        self.region_info = config.qcloud_region_info
        self.bucket = u'tszins001'
        self.os_path = u'/'
        self.cdn = u'https://cdn.tszins.tv/'
    def connection(self):
        cos_client = qcloud_cos.CosClient(appid=self.appid,secret_id=self.secret_id,secret_key=self.secret_key,region=self.region_info)
        return cos_client
    def list_floder(self):
        cos_client = self.connection()
        dirlist=[]
        def get(name=''):
            request = cos_request.ListFolderRequest(bucket_name=self.bucket, cos_path=self.os_path + name)
            res = cos_client.list_folder(request)
            infos = res['data']['infos']
            if infos:
                for obj in infos:
                    name1 = obj['name']
                    if name1[-1] == '/':
                        name2=name+name1
                        get(name2)
                    else:
                        dirlist.append(self.cdn+name+name1)
        get()
        return dirlist
