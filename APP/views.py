#!/usr/bin/env python
# -*- coding: utf-8 -*-
from APP import app
import os,hashlib,json
from flask import render_template
from flask import abort, redirect, url_for,session,escape,request
from functools import wraps
from luoweis.object_storage import object_storage
from luoweis.tszins_redis import tszins_redis
from luoweis.qcloud import qcloud_tszins
#引入全局配置文件
import luoweis.config
from werkzeug.utils import secure_filename
#redis session
from luoweis.tszins_session import RedisSessionInterface

#定义过滤器
#过滤器 keySize
#返回文件的大小 Kb 或 Mb
@app.template_filter('keySize')
def keySize(value,B):

    if float(value)/(B**3) >=1:
        res = ('%.1f%s'%((float(value)/(B**3)),'GB'))
    elif float(value)/(B**2) >=1:
        res = ('%.1f%s' % ((float(value) / (B ** 2)), 'MB'))
    else:
        res = ('%.1f%s'%((float(value)/(B)),'KB'))
    return res
@app.template_filter('fileType')
def fileType(file):
    html5Video=['mp4','ogv','webm']
    html5Picture=['gif','png','jpg']
    res = file.split('.')[-1]#以点为分隔符
    if res in html5Video:
        return 'video'
    elif res in html5Picture:
        return 'picture'
    else:
        return 'others'
@app.template_filter('qcloudFilter1')
def qcloudFilter1(cdn):
    m1 = hashlib.md5()
    m1.update(cdn)
    res = m1.hexdigest()
    return res
@app.template_filter('qcloudFilter2')
def qcloudFilter2(something):
    coludView=['png','jpg','jpeg','gif']
    temp = something.split('.')
    if temp[-1] in coludView:
        return True
    else:
        return False
''' --以上是定义的过滤器-- '''
#定义session的接口方式，这里将session统一存储到redis数据库中。session的有效期为1天
app.session_interface = RedisSessionInterface()
ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','jpeg','gif','mp4','ogv','webm'])
app.config['UPLOAD_FOLDER'] = luoweis.config.UPLOAD_FOLDER
#验证登录的装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'user' not in session:
            #return redirect(url_for('login',next=request.url))
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return decorated_function
#验证上传的文件类型
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

#实例化对象
objs = object_storage()
tszins_redis = tszins_redis()

#登录login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        m1 = hashlib.md5()
        m1.update(password)
        if username =='':
            return redirect(url_for('login'))
        if luoweis.config.admins.has_key(username) and  m1.hexdigest() == luoweis.config.admins[username]['password']:
            session['user']  = luoweis.config.admins[username]
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')
#退出登录
@app.route('/logout')
@login_required
def lougout():
    #将用户信息在session中删除
    session.pop('user',None)
    #return render_template('login.html')
    return redirect('/login')
#修改密码
@app.route('/userchange')
@login_required
def userchange():
    username = session['user']['username']
    luoweis.config.admins[username]['password'] = ''
#
@app.route('/')
@login_required
def index():
    buckets = objs.bucketsList()
    return render_template('index.html',buckets = buckets,total_save = luoweis.config.ceph_save_total_KB)
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
@app.route('/keyUpload/<bucket>',methods=['POST'])
@login_required
def keyUpload(bucket):
    if request.method=='POST':
        tag = request.form['tag']
        file = request.files['file']
        acl = request.form['acl']
        group = request.form['group']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #首先判断redis数据库中是否有该filename
            if tszins_redis.keyExistsInHset(bucket,filename):
                return redirect(url_for('index'))
            else:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))#保存到本地路径中
                file_size = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], filename)).st_size#统计文件的大小
                source_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)#这里添加文件夹头部信息如：/test/
                redis_value ={"size": file_size, "tag": tag,"group":group}
                if file_size >= 52428800:
                    res = objs.keyCreate(bucket,source_path,file_size)
                    if res:
                        # 上传完之后赋予上传的key指定的权限
                        objs.acl_create(bucket, filename,acl=acl)
                        #将文件名字写入redis数据库中
                        tszins_redis.keyToRedisUseHset(bucket,filename,redis_value)
                        #统计bucket的key的大小
                        tszins_redis.bucketSize(bucket,file_size)
                        #上传完成后清空上传的文件
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                        #return redirect(url_for('listKeys',bucket=bucket))
                        return 'ok'
                else:
                    res = objs.keyCreateSmall(bucket,filename,source_path)
                    if res:
                        # 上传完之后赋予上传的key指定的权限
                        objs.acl_create(bucket, filename,acl=acl)
                        # 将文件名字写入redis数据库中
                        tszins_redis.keyToRedisUseHset(bucket,filename, redis_value)
                        # 统计bucket的key的大小
                        tszins_redis.bucketSize(bucket, file_size)
                        # 上传完成后清空上传的文件
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        #return redirect(url_for('listKeys',bucket=bucket))
                        return 'ok'

##定义一个用来检查上传的文件是否已经存在的路由
@app.route('/filenameCheck/<bucket>')
@login_required
def filenameCheck(bucket):
    filename = request.args['file']
    res = tszins_redis.keyExistsInHset(bucket, filename)
    if res:
        return 'ok'
    else:
        return 'no'

#创建一个bucket
@app.route('/addBucket')
@login_required
def addBucket():
    bucket = request.args['bucket']
    objs.bucketCreate(bucket)
    return 'ok'
#删除一个bucket
@app.route('/delBucket')
@login_required
def delBucket():
    bucket = request.args['bucket']
    objs.bucketDel(bucket)
    return 'ok'

#列出指定的bucket下所有的key
@app.route('/list/<bucket>')
@login_required
def listKeys(bucket):
    keys = objs.keysList(bucket)
    return render_template('keys.html',bucket = bucket,keys = keys)
#
@app.route('/geturl/<bucket>')
@login_required
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
#删除指定bucket中的key
@app.route('/key/delete/<bucket>')
@login_required
def deleteKey(bucket):
    key = request.args['key']
    size = request.args['size']
    #从ceph中删除
    objs.deleteKey(bucket,key)
    #从redis数据库中删除
    tszins_redis.keyDeleteFromHset(bucket,key)
    #redis中记录的存储占用量删除
    r = tszins_redis.connection()
    r.decr(bucket+'_size',size)
    return key
#邮箱验证的本地方法，邮箱是写死在程序中的
@app.route('/confirmEmail',methods=['POST'])
@login_required
def confirmEmail():
    askEmail = request.json.get('email')#前端通过POST传递过来的json数据，通过这种方法提取数据
    if luoweis.config.adminsEmail.has_key(askEmail) and luoweis.config.adminsEmail[askEmail] == session['user']['username']:
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
    #return  render_template('play.html',url=url)
    return url

@app.route('/playOnPhone/<bucket>')
def playVideoOnPhone(bucket):
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
        res = qcloud.modifity_key(key,seconds,ID,title,sub_title,cname,cdate)
        return "ok"
    else:
        return 'ERROR'
        #
        #
        #r = tszins_redis.connection()
        #r.hset('qcloud_time',key,biz_attr)
        #return 'ok'
######-------------- single  test-----------###
@app.route('/redistest')
def testSingle():
    res = json.dumps(tszins_redis.keyFromRedisUseHset('qcloud_time'))
    # res = tszins_redis.keyExistsInHset('606007.gif')
    # if res:
    #     return "yes"
    # else:
    #     return 'no'
    return res

@app.route('/single1')
def single1():
    qcloud = qcloud_tszins()
    res = qcloud.list_floder_video()
    res = sorted(res.iteritems(), key=lambda d: d[0])
    return repr(res)

@app.route('/single2')
def single2():
    qcloud = qcloud_tszins()
    res = qcloud.key_info(u'https://cdn.tszins.tv/taoyongjun/20160918/TYJ_20160918_0001_360P.mp4')
    return repr(res)