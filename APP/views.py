#!/usr/bin/env python
# -*- coding: utf-8 -*-
from APP import app
import os,json
from flask import render_template
from flask import abort, redirect, url_for,session,escape,request
from functools import wraps
from luoweis.object_storage import object_storage
from luoweis.confirm_email import adminsEmail
import hashlib
from werkzeug.utils import secure_filename

#定义上传的路径等参数
UPLOAD_FOLDER='/Users/luoweis/tszins'
ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','jpeg','gif','mp4','ogv','webm'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#验证登录的装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'username' not in session:
            return redirect(url_for('login',next=request.url))
        return f(*args,**kwargs)
    return decorated_function
#验证上传的文件类型
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS


objs = object_storage()
#登录login
@app.route('/login',methods=['GET','POST'])
def login():
    password_md5 = 'a44df41524d1b7198e6e2c3cda445caf'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        m1 = hashlib.md5()
        m1.update(password)
        if username =='':
            return redirect(url_for('login'))
        if username =='luoweis' and  m1.hexdigest() == password_md5:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')
#退出登录
@app.route('/logout')
def lougout():
    #将用户名从session中剔除
    session.pop('username',None)
    return redirect(url_for('index'))
#
@app.route('/')
@login_required
def index():
    buckets = objs.bucketsList()
    return render_template('index.html',buckets = buckets)
#上传接口
#上传到服务器的本地硬盘上
@app.route('/upload',methods=['POST'])
@login_required
def upload():
    if request.method=='POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            return redirect(url_for('index'))
#上传接口2
#上传到bucket中
#上传方式区分文件的大小
#以50MiB为基准
@app.route('/keyUpload/<bucket>',methods=['GET','POST'])
@login_required
def keyUpload(bucket):
    if request.method=='POST':
        file = request.files['file']
        acl = request.form['acl']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))#保存到本地路径中
            file_size = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], filename)).st_size#统计文件的大小
            source_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
            if file_size >= 52428800:
                objs.keyCreate(bucket,source_path,file_size)
                # 上传完之后赋予上传的key指定的权限
                objs.acl_create(bucket, filename,acl=acl)
                return redirect(url_for('index'))
            else:
                objs.keyCreateSmall(bucket,filename,source_path)
                # 上传完之后赋予上传的key指定的权限
                objs.acl_create(bucket, filename,acl=acl)
                return redirect(url_for('index'))

#创建一个bucket
@app.route('/bucket/create')
def creat_bucket():
    bucket = 'tszins-for-luoweis2'
    objs.bucketCreate(bucket)
    return redirect(url_for('list_buckets'))
#列出指定的bucket下所有的key
@app.route('/list/<bucket>')
@login_required
def list_keys(bucket):
    keys = objs.keysList(bucket)
    return render_template('keys.html',bucket = bucket,keys = keys)
#
@app.route('/geturl/<bucket>')
def geturl(bucket):
    key = request.args['key']
    choose = request.args['choose']
    if choose=='READ':
        url = objs.GetKeyUrl(bucket,key,private=False)
        return url
    elif choose=='private':
        url = objs.GetKeyUrl(bucket,key,private=True)
        return url
    else:
        pass
#将key从存储集群下载到服务器指定的目录上
@app.route('/key/download')
def download_key():
    bucketName = 'tszins-for-luoweis1'
    keyName = 'testluoweis1.jpg'
    objs.keyDownload(bucketName,keyName)
    return redirect(url_for('list_keys'))
#更改key的权限
@app.route('/key/ACL')
def publicRead_ACL():
    bucketName = 'tszins-for-luoweis'
    keyName = '11106263081.gif'
    objs.acl_read(bucketName,keyName)
    return 'ok'
#删除指定bucket中的key
@app.route('/key/delete/<bucket>')
def deleteKey(bucket):
    key = request.args['key']
    objs.deleteKey(bucket,key)
    return key
#邮箱验证的本地方法，邮箱是写死在程序中的
@app.route('/confirmEmail')
@login_required
def confirmEmail():
    askEmail = request.args['email']
    if adminsEmail.has_key(askEmail) and adminsEmail[askEmail] == session['username']:
        return 'ok'
    else:
        return 'error'
#获取指定的key的http地址然后在html5中播放
#html5 支持的播放视频格式为 mp4 ogv webm
@app.route('/play/<bucket>')
@login_required
def playVideo(bucket):
    key = request.args['key']
    acl = request.args['acl']
    url=''
    if acl=='READ':
        url = objs.GetKeyUrl(bucket,key,private=False)
    elif acl=='private':
        url = objs.GetKeyUrl(bucket,key,private=True)
    else:
        pass
    return  render_template('play.html',url=url)