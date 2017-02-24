#!/usr/bin/env python
# -*- coding: utf-8 -*-
from APP import app
from flask_mail import Mail,Message
from flask import request
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
app.config.update(
    MAIL_SERVER='smtp.126.com',
    MAIL_PROT=25,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME="luoweis@126.com",
    MAIL_PASSWORD="P@ssword",
)

mail = Mail(app)
#url /sendEmail?email=luoweis@126.com
@app.route('/sendEmail',methods=['POST'])
def sendEmail():
    who = request.json.get('who')#前端通过POST传递过来的json数据，通过这种方法提取数据
    html = request.json.get('html')
    msg = Message('来自青岛三藏信息技术有限公司_From TszinS',
                  sender='luoweis@126.com',
                  recipients=[who]
                  )
    #msg.body 邮件正文
    msg.html = html
    #msg.attach邮件附件添加
    # msg.attach("文件名", "类型", 读取文件）
    #with app.open_resource('/Users/luoweis/Tszins.png') as fp:
    #    msg.attach('Tszins.png','image/png',fp.read())

    mail.send(msg)
    return "ok"
