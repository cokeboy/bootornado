#!/usr/bin/env python
#coding=utf-8
"""
    views: base.py
"""
import os

import logging
import tornado.web
import tornado.locale
import tornado.escape
import urlparse

from sessions.session import SessionMixin

from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter

try:
    from urllib import urlencode  # py2
except ImportError:
    from urllib.parse import urlencode  # py3


class FlashMessageMixIn(object):
    """
        Store a message between requests which the user needs to see.

        views
        -------

        self.flash("Welcome back, %s" % username, 'success')

        base.html
        ------------
        
        {% set messages = handler.get_flashed_messages() %}
        {% if messages %}
        <div id="flashed">
            {% for category, msg in messages %}
            <span class="flash-{{ category }}">{{ msg }}</span>
            {% end %}
        </div>
        {% end %}
    """
    def flash(self, message, category='message'):
        messages = self.messages()
        messages.append((category, message))
        self.set_secure_cookie('flash_messages', tornado.escape.json_encode(messages))
    
    def messages(self):
        messages = self.get_secure_cookie('flash_messages')
        messages = tornado.escape.json_decode(messages) if messages else []
        return messages
        
    def get_flashed_messages(self):
        messages = self.messages()
        self.clear_cookie('flash_messages')
        return messages
class RequestHandler(tornado.web.RequestHandler,  FlashMessageMixIn,SessionMixin):
    def get_error_html(self, status_code, **kwargs):
        if self.settings.get('debug', False) is False:
            self.set_status(status_code)
            return self.render_string('errors/%s.html' % status_code)

        else:
            def get_snippet(fp, target_line, num_lines):
                if fp.endswith('.html'):
                    fp = os.path.join(self.get_template_path(), fp)

                half_lines = (num_lines/2)
                try:
                    with open(fp) as f:
                        all_lines = [line for line in f]
                        code = ''.join(all_lines[target_line-half_lines-1:target_line+half_lines])
                        formatter = HtmlFormatter(linenos=True, linenostart=target_line-half_lines, hl_lines=[half_lines+1])
                        lexer = get_lexer_for_filename(fp) 
                        return highlight(code, lexer, formatter)
                
                except Exception, ex:
                    logging.error(ex)
                    return ''

            css = HtmlFormatter().get_style_defs('.highlight')
            exception = kwargs.get('exception', None)
            return self.render_string('exception.htm', 
                                      get_snippet=get_snippet,
                                      css=css,
                                      exception=exception,
                                      status_code=status_code, 
                                      kwargs=kwargs)
    
    def get_args(self, key, default=None, type=None):
        if type==list:
            if default is None: default = []
            return self.get_arguments(key, default)
        value = self.get_argument(key, default)
        if value and type:
            try:
                value = type(value)
            except ValueError:
                value = default
        return value
    
    @property
    def is_xhr(self):
        '''True if the request was triggered via a JavaScript XMLHttpRequest.
        This only works with libraries that support the `X-Requested-With`
        header and set it to "XMLHttpRequest".  Libraries that do that are
        prototype, jQuery and Mochikit and probably some more.'''
        return self.request.headers.get('X-Requested-With', '') \
                           .lower() == 'xmlhttprequest'


class GeneralHandler(RequestHandler):
    def get_current_user(self):
        return None

class FrontHandler(RequestHandler):
    def get_template_path(self):
        return os.path.join(self.settings.get('template_path'),"front")
class AdminHandler(RequestHandler):
    def get_template_path(self):
        return os.path.join(self.settings.get('template_path'),"admin")
        
class AsynAuthHandler(RequestHandler):
    '''
        you shuld use _get_,_post_,_put_,_delete_ and self.finish() end.
    '''
    @tornado.web.asynchronous 
    @tornado.gen.engine
    def get(self,*args,**kwargs):
        if not hasattr(self,'_get_'):
            raise tornado.web.HTTPError(405)   
        userinfo = yield tornado.gen.Task( self.session.get,'userinfo' )
        if not userinfo:
            url = self.get_login_url()
            if "?" not in url:
                if urlparse.urlsplit(url).scheme:
                    # if login url is absolute, make next absolute too
                    next_url = self.request.full_url()
                else:
                    next_url = self.request.uri
                url += "?" + urlencode(dict(next=next_url))
            self.redirect(url)
            return 
        self._get_(*args,**kwargs)
    @tornado.web.asynchronous 
    @tornado.gen.engine
    def post(self,*args,**kwargs):
        if not hasattr(self,'_post_'):
            raise tornado.web.HTTPError(405)   
        userinfo = yield tornado.gen.Task( self.session.get,'userinfo' )
        if not userinfo:
            raise tornado.web.HTTPError(403) 
        self._post_(*args,**kwargs)
    @tornado.web.asynchronous 
    @tornado.gen.engine
    def put(self,*args,**kwargs):
        if not hasattr(self,'_put_'):
            raise tornado.web.HTTPError(405)   
        userinfo = yield tornado.gen.Task( self.session.get,'userinfo' )
        if not userinfo:
            raise tornado.web.HTTPError(403) 
        self._put_(*args,**kwargs)
    @tornado.web.asynchronous 
    @tornado.gen.engine
    def delete(self,*args,**kwargs):
        if not hasattr(self,'_delete_'):
            raise tornado.web.HTTPError(405)   
        userinfo = yield tornado.gen.Task( self.session.get,'userinfo' )
        if not userinfo:
            raise tornado.web.HTTPError(403) 
        self.userinfo = userinfo
        self._delete_(*args,**kwargs)
    def get_userinfo_ext(self):
        return {
            'appkey'    : 'appkey',
            'parent_id' : 'parent_id',
        }
class FrontAsynAuthHandler(AsynAuthHandler,FrontHandler):
    pass
class AdminAsynAuthHandler(AsynAuthHandler,AdminHandler):
    pass
        
class ErrorHandler(RequestHandler):
    """raise 404 error if url is not found.
    fixed tornado.web.RequestHandler HTTPError bug.
    """
    def get_template_path(self):
        return self.settings.get('template_path')
    def prepare(self):
        self.set_status(404)
        raise tornado.web.HTTPError(404)


