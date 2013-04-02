#!/usr/bin/env python
#coding=utf-8
"""
    views: web.py
"""
import simplejson
import logging
import tornado.web
import tornado.escape

from datetime import datetime
from tornado_utils.routes import route

from bootornado.views.base import FrontAsynAuthHandler,FrontHandler


@route(r'/', name='index')
class Index(FrontAsynAuthHandler):
    def _get_(self):
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

        self.session_end()
        self.render("index.html", 
                    page_obj = page_obj,
                    page_url = page_url)
@route(r'/auth/login',name='auto.login')
class AuthLogin(FrontHandler):
    def get(self):
        page_obj = []        
        page_url = None
        self.render("index.html", 
                    page_obj = page_obj,
                    page_url = page_url)
        