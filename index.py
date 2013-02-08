import webapp2,json,os,datetime,urllib

from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import taskqueue

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Home!')

class InitIcon(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain';
		
		taskqueue.add(url='/icon/'
		,params={'keyName':"ucon://toolset/camera",'thumb':"http://cache.gawker.com/assets/images/lifehacker/2011/07/1030-camplus-icon.jpg", 'type': 'camera', 'tag':'toolset' , 'content': '{}' } 
		,queue_name='fastAndSecure');
		#upload photo app
		taskqueue.add(url='/icon/'
		,params={'keyName':"ucon://toolset/upload-photo", 'thumb':"http://cdn1.iconfinder.com/data/icons/iVista2/256/Upload.png", 'type': 'camera', 'tag':'toolset' , 'content': json.dumps({"sourceType":"PhotoLibrary"}) } 
		,queue_name='fastAndSecure');
		
		self.response.out.write('OK!')
			

app = webapp2.WSGIApplication([
('/init',InitIcon),
('/[^/]*', MainPage)
])
