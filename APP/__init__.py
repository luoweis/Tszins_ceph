from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

import APP.views,APP.luoweis.sendEmail
import APP.qcloud.qcloudManage