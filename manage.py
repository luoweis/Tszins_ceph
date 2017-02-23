#!/usr/bin/env python
# -*- coding: utf-8 -*-
from APP import app
#定义编码格式为unicode utf-8 默认的编码格式是ascii
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


app.debug=True
app.run(host='0.0.0.0',port=8080)
