#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
from datetime import timedelta
from uuid import uuid4
from tszins_redis import tszins_redis
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin
import sys
reload(sys)

'''
Flask 默认的session是将cookie 内容保存到内存中，而session是单进程，如果我们在实际生产环境下部署Flask，使用的Gunicorn作为uwsgi，启动多进程
的时候，这时候就会出现一种现象，要求你反复登录。因为session不是进程间共享的。
所以这里就使用Redis作为session的存储，能够在多进程和多服务器间做到共享。
Redis session 有效期为1天
so enjoy it!
'''
class RedisSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    serializer = pickle
    session_class = RedisSession

    def __init__(self, redis=None, prefix='session:'):
        if redis is None:
            Tredis = tszins_redis()#使用自己封装的redis
            redis = Tredis.connection()
        self.redis = redis
        self.prefix = prefix

    def generate_sid(self):
        return str(uuid4())

    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        val = self.redis.get(self.prefix + sid)
        if val is not None:
            data = self.serializer.loads(val)
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            self.redis.delete(self.prefix + session.sid)
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
            return
        redis_exp = self.get_redis_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.prefix + session.sid, val,
                         int(redis_exp.total_seconds()))
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True,
                            domain=domain)