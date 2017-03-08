#!/usr/bin/env python
# -*- coding: utf-8 -*-
from APP import app
import qcloud_cos
from qcloud_cos import cos_request
import config
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')

class qcloud_tszins():
    def __init__(self,os_path=u'/'):
        self.appid = config.qcloud_appid
        self.secret_id = config.qcloud_secret_id
        self.secret_key = config.qcloud_secret_key
        self.region_info = config.qcloud_region_info
        self.bucket = u'tszins001'
        self.os_path = os_path
        self.cdn = u'https://cdn.tszins.tv/'
    def connection(self):
        cos_client = qcloud_cos.CosClient(appid=self.appid,secret_id=self.secret_id,secret_key=self.secret_key,region=self.region_info)
        return cos_client
    def list_floder_video(self):
        cos_client = self.connection()
        dirdict = {}
        def get(name=''):
            request = cos_request.ListFolderRequest(bucket_name=self.bucket, cos_path=self.os_path + name)
            res = cos_client.list_folder(request)
            infos = res['data']['infos']
            if infos:
                for obj in infos:
                    name1 = obj['name']
                    if name1 == 'tszins_cms/':
                        pass
                    elif name1== 'tszins_weixin/' or name1 == 'test/':
                        pass
                    else:
                        if name1[-1] == '/':
                            name2=name+name1
                            get(name2)
                        else:
                            key = self.cdn+name+name1
                            res = self.key_info(key)
                            dirdict[key] = res['data']
        get()
        return dirdict
    def list_floder_cms(self):
        cos_client = self.connection()
        dirdict = {}
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
                        key = self.cdn+u'tszins_cms/'+name+name1
                        res = self.key_info(key)
                        dirdict[key] = res['data']
        get()
        return dirdict
    def key_info(self,key):
        cos_client = self.connection()
        cos_path = key.replace('https://cdn.tszins.tv','')
        request = cos_request.StatFileRequest(self.bucket, cos_path=cos_path)
        res = cos_client.stat_file(request)
        return res
    def modifity_key(self,key,seconds,ID,title,sub_title,cname,cdate):
        cos_client = self.connection()
        cos_path = key.replace('https://cdn.tszins.tv', '')
        request = cos_request.UpdateFileRequest(self.bucket,cos_path=cos_path)
        #request.set_biz_attr(biz_attr)
        request.set_x_cos_meta(u'x-cos-meta-seconds',unicode(seconds))
        request.set_x_cos_meta(u'x-cos-meta-ID', unicode(ID))
        request.set_x_cos_meta(u'x-cos-meta-title', unicode(title))
        request.set_x_cos_meta(u'x-cos-meta-subtitle', unicode(sub_title))
        request.set_x_cos_meta(u'x-cos-meta-cname', unicode(cname))
        request.set_x_cos_meta(u'x-cos-meta-cdate', unicode(cdate))
        #信息被写入到custom_headers中
        #{u'message': 'x-cos-meta-value is not unicode!', u'code': -1}
        res = cos_client.update_file(request)
        print res


    #------------------------------------#