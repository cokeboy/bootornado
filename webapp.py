import web
     
web.config.debug = False   
urls = (
	"/count", "count",
    "/reset", "reset",
    '/(.*)', 'hello'
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'count': 0})

class count:
    def GET(self):
    	if 'count' in session:
    		session.count += 1
    	session.count = 1
        return str(session.count)

class reset:
    def GET(self):
        session.kill()
        return ""

class hello:        
    def GET(self, name):
        if not name: 
            name = 'World'
        return 'Hello, ' + name + '!'

if __name__ == "__main__":
    app.run()