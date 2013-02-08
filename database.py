import os
import datetime,json
import urllib

from google.appengine.ext import db

from google.appengine.api import users
from google.appengine.api import mail

def dictJSON(obj):
	""" Convert a db.Model object into a JSON dictionary
	"""
	jsonDict={};
#	for property, value in vars(obj).iteritems():
#		jsonDict.setdefault(property,str(value));
	for property in obj._entity:
		value=obj._entity[property];
		if isinstance(value,datetime.datetime):
			value=str(value);
		if isinstance(value,users.User):
			value=str(value.email());
		if isinstance(value,db.GeoPt):
			value=str(value);
		jsonDict.setdefault(property,value);
	jsonDict.setdefault('key', str(obj.key()) );
	jsonDict.setdefault('key_name', obj.key().name() );
	
	return jsonDict;
	
class Icon(db.Model):
	"""Models an individual Icon """
	created = db.DateTimeProperty(auto_now_add=True);
	whoCreated = db.UserProperty(auto_current_user_add=True);
	whereCreated = db.GeoPtProperty();
	
	modified = db.DateTimeProperty(auto_now=True);
	whoModified = db.UserProperty(auto_current_user=True);
	whereModified = db.GeoPtProperty();
	
	thumb = db.TextProperty(default="http://akensai.com/wp-content/plugins/thumbnail-for-excerpts/tfe_no_thumb.png");
	type = db.StringProperty();
	tag = db.ListProperty(str,default=[]);
	
	#these 2 not yet used
	sharingMode = db.StringProperty(choices=set(['public','private']),default='public') ;
	accessUsers = db.ListProperty(users.User,default=[]); # (those have access to icon in private mode) 
	
	content = db.TextProperty(default='{}');
	
	def dictJSON(self):
		return dictJSON(self);

		

class Action(db.Model):
	"""Models an individual Action """
	created = db.DateTimeProperty(auto_now_add=True);
	whoCreated = db.UserProperty(auto_current_user_add=True);
	whereCreated = db.GeoPtProperty();
	
	modified = db.DateTimeProperty(auto_now=True);
	whoModified = db.UserProperty(auto_current_user=True);
	
	place = db.StringProperty();
	type = db.StringProperty();
	tag = db.ListProperty(str,default=[]);
	
	iconID = db.StringProperty();
	content = db.TextProperty(default='{}');
	
	def dictJSON(self):
		return dictJSON(self);
