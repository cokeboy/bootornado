#!/usr/bin/env python
#coding=utf-8
"""
    bootornado Application
    ~~~~~~~~~~~
    :author: xiao.lin@163.com
"""
import os

#!/usr/bin/env python
#coding=utf-8
import tornado.web
import tornado.locale

from tornado.web import url
from tornado_utils.routes import route

import bootornado.session
from bootornado import uimodules

from bootornado.views.web import *

class Application(tornado.web.Application):
    def __init__(self):
        handlers = route.get_routes()

        settings = dict(
            title = "bootornado",
            template_path = os.path.join(os.path.dirname(__file__),"templates"),
            static_path = os.path.join(os.path.dirname(__file__),"static"),
            debug = True,
            ui_modules = uimodules,
            autoescape = None,
            cookie_secret = "bootornado"
        )
        self.session = bootornado.session.Session(bootornado.session.DiskStore('sessions'), initializer={'count': 0})
        tornado.web.Application.__init__(self, handlers, **settings)