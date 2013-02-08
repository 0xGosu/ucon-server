import os
import datetime
import urllib,json

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.api import taskqueue

from database import Icon
import tool;

class MainPage(webapp.RequestHandler):
	def get(self):
		self.error(404);
		
class Login(webapp.RequestHandler):
	def get(self):
		ENV=tool.readHeader(self.request);
		user=ENV.CurrentUser;
		if user:
			#check and create icon user automaticly
			self.checkAndCreateIconAutomatic();
			self.response.out.write("Login Success")
			
		else:
			if self.request.get('check'):
				self.response.out.write("Not yet Login")
			else:
				url = users.create_login_url(self.request.uri)
			self.redirect(url);

	def checkAndCreateIconAutomatic(self):
		ENV=tool.readHeader(self.request);
		user=ENV.CurrentUser;
		keyName='ucon://user/'+user.email();
		userIcon=db.get(db.Key.from_path('Icon',keyName ));
		if not userIcon:
			userIcon=Icon(key_name=keyName);
			userIcon.thumb="http://wwwcdn.net/ev/assets/images/vectors/afbig/user-symbol-blue-clip-art.jpg";
			userIcon.type='user';
			#generate content;
			contentDict={
			'photoURL' :userIcon.thumb , 
			'facetimeID' : user.email(),
			'email' : user.email(),
			'home' : keyName+'/public/home',
			'inbox' : keyName+'/private/inbox',
			'item'	: keyName+'/private/item',
			};	
			userIcon.whereCreated=ENV.CityLatLong;
			userIcon.whereModified=ENV.CityLatLong;
			
			
			itemBarPlaceName=keyName+'/private/item';
			## need: add task (makecopy of toolset icon to user item bar)
			#camera app, upload-photo app
			contentDict['toolset']=["ucon://toolset/camera","ucon://toolset/upload-photo"];
			
			taskqueue.add(url='/icon/'
			,params={'keyName':'ucon://place/'+contentDict.get('home'), 'thumb':"http://theparentplace.files.wordpress.com/2012/04/home1.png", 'type': 'place', 'tag':'home' , 
			'content': json.dumps({
			"placeName": contentDict.get('home'), 
			"title": user.email() + " - Home", 
			"backgroundPhotoURL": "", 
			"photoURL": userIcon.thumb
			})
			}
			,queue_name='fastAndSecure');
			
#			taskqueue.add(url='/action/'
#			,params={'place':itemBarPlaceName, 'type': 'makecopy', 'tag':'toolset' , 'content': json.dumps({"iconID":"ucon://toolset/camera","isKeyName":True}) } 
#			,queue_name='fastAndSecure');
#			#upload photo app
#			taskqueue.add(url='/action/'
#			,params={'place':itemBarPlaceName, 'type': 'makecopy', 'tag':'toolset' , 'content': json.dumps({"iconID":"ucon://toolset/upload-photo","isKeyName":True}) } 
#			,queue_name='fastAndSecure');

			userIcon.content = json.dumps(contentDict);
			userIcon.put();
		
class Logout(webapp.RequestHandler):
	def get(self):
		ENV=tool.readHeader(self.request);
		user=ENV.CurrentUser;
		if not user:
			self.response.out.write("Logout Success")
		else:
			url = users.create_logout_url(self.request.uri)
			self.redirect(url);
			
#def main():
app = webapp.WSGIApplication([
('/auth/[^/]*', MainPage),
('/auth/login/[^/]*', Login),
('/auth/logout/[^/]*', Logout),
], debug=True)

#	util.run_wsgi_app(application)
#
#
#if __name__ == '__main__':
#	main()
