#!/usr/bin/env python
#coding=utf-8


import tornado.httpserver
import tornado.ioloop
import tornado.options

from tornado.options import define, options 

from bootornado import Application

define("cmd", default='run', 
        metavar="run",
        help=("Default use runserver"))
define("port", default=9000, help="default: 9000, required runserver", type=int)

def main():
    tornado.options.parse_command_line()

    if options.cmd == 'run':
        print 'server started. port %s' % options.port
        http_server = tornado.httpserver.HTTPServer(Application())
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()

    else:
        print 'error cmd param: python app.py --help'

if __name__=='__main__':
    main()

