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

from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter

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

class RequestHandler(tornado.web.RequestHandler,  FlashMessageMixIn):
    def initialize(self):
        self.session = self.application.session
        
    def prepare(self):
        self.session.session_start(self)

    def on_finish(self):
        """sqlalchemy connection close. 
        fixed sqlalchemy error: 'Can't reconnect until invalid'. new in version 2.2"""
        #db.session.remove()
        print "on_finish"
        self.session.session_end()

    def get_current_user(self):
        user =  None
        return user
    
    
    def get_template_path(self):
        if 'theme_path' in self.settings:
            return os.path.join(self.settings['theme_path'], self.settings.get('theme_name', 'default'), 'templates')
        return self.settings.get('template_path')
    
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

 
class ErrorHandler(RequestHandler):
    """raise 404 error if url is not found.
    fixed tornado.web.RequestHandler HTTPError bug.
    """
    def prepare(self):
        self.set_status(404)
        raise tornado.web.HTTPError(404)


