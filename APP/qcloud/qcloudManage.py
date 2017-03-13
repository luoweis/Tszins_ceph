#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import json
import os
from functools import wraps

from flask import redirect, url_for,session, request
from flask import render_template
from APP import app
from qcloud import qcloud_tszins


#验证登录的装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'user' not in session:
            #return redirect(url_for('login',next=request.url))
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return decorated_function

#qcloud
@app.route('/qcloud/video')
@login_required
def qcloud():
    qcloud = qcloud_tszins()
    res = qcloud.list_floder_video()
    return render_template('qcloud.html',qcloud=res)
@app.route('/qcloud/tszins_cms')
@login_required
def qcloud_cms():
    qcloud = qcloud_tszins(u'/tszins_cms/')
    res = qcloud.list_floder_cms()
    return render_template('qcloud_cms.html',qcloud=res)
@app.route('/playOnPhoneQcloud')
def playOnPhoneQcloud():
    url = request.args['cdn']
    return render_template('play.html',url = url)

@app.route('/cloudTag',methods=['GET','POST'])
@login_required
def cloudTag():
    if request.method == "POST":
        time = request.form['seconds']
        ID = request.form['ID']
        title = request.form['title']
        sub_title = request.form['subtitle']
        key = request.form['key']
        cname = request.form['cname']
        cdate = request.form['cdate']
        if ':' in time:
            temp = time.split(':')
            seconds = (int(temp[0])*60+int(temp[1]))
        else:
            seconds = time
        qcloud = qcloud_tszins()
        print time,ID,title,sub_title,key,cname,cdate
        res = qcloud.modifity_key(key,seconds,ID,title,sub_title,cname,cdate)
        if res == 'ok':
            return "ok"
        else:
            return 'error'
    else:
        return 'ERROR'