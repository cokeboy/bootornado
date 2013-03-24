#!/usr/bin/env python
#coding=utf-8
"""
    views: blog.py
"""
import simplejson
import logging
import tornado.web
import tornado.escape

from datetime import datetime
from tornado_utils.routes import route

from bootornado.views.base import RequestHandler

@route(r'/', name='index')
class Index(RequestHandler):
    def get(self):
        page_obj = []        
        page_url = None
        user_id  = None
        if "user_id" in self.session:
        	logging.error( self.session["user_id"] )
        	user_id = self.session["user_id"]
        if user_id:
        	user_id = user_id + "_" + user_id
        else:
        	user_id = "xxxxx"
        self.session["user_id"] = user_id
        self.render("index.html", 
                    page_obj = page_obj,
                    page_url = page_url)
        return