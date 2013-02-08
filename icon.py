import os
import datetime,json
import urllib


from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from google.appengine.api import datastore_errors;


from google.appengine.api import users
from google.appengine.api import mail

class Custom():
	pass


from database import Icon
import tool		

class GetIcon(webapp.RequestHandler):
	
	def get(self):
		ENV=tool.readHeader(self.request);		
		
		#Get var from request
		
		matchCurrentUser = self.request.get('createdByMe');
		
		type=self.request.get_all('type')
		tags=self.request.get_all('tag');
		
		maxFetch=self.request.get_range('max',0,100,default=1);
		offset=self.request.get_range('offset',0,10000,default=0);
		
		keys_only=self.request.get('keys_only');
		
		callbackJSONP=self.request.get('JSONP');
		
		#Query
		if(keys_only):query = db.Query(Icon, keys_only=True);
		else:query = db.Query(Icon, keys_only=False);
		
		#Filter
		if matchCurrentUser:
			query.filter("whoCreated =", ENV.CurrentUser);
		if type:
			query.filter("type IN", type);
		for tag in tags:
			if tag:query.filter("tag =", tag);
		
		#Fetch
		data=[];
		if maxFetch>0:
			data = query.fetch(maxFetch,offset);
		else:
			data = [entry for entry in query];
				
		#reversed, most new at bottom
#		entries=reversed(data);
		
		#render
		if(keys_only):
			jsonData=json.dumps( [entry for entry in data]) ;
		else:
			jsonData=json.dumps( [entry.dictJSON() for entry in data]) ;
		if callbackJSONP:
			self.response.out.write(callbackJSONP+'('+jsonData+');');
		else: self.response.out.write(jsonData);
		
		return;

	def post(self):
		ENV=tool.readHeader(self.request);
		#Get var from request and pass to data model object
		keyName=self.request.get('keyName');
		callbackJSONP=self.request.get('JSONP');
		if keyName: 
			entry = db.get(db.Key.from_path('Icon',keyName ));
			if entry==None: 
				entry = Icon(key_name=keyName)
			else:
				#keyName exist
				self.response.out.write(json.dumps([]));
		else: entry= Icon();
		
		#pass to model
		try:	
			#check valid json , save as python json
			entry.content=json.dumps( json.loads(self.request.get('content')) );
		except ValueError:
			self.response.out.write(json.dumps([]));	
			return;
		
		entry.thumb = self.request.get('thumb');
		entry.type = self.request.get('type');
		d={};#temporary dict
		entry.tag = [d.setdefault(tag,tag) for tag in self.request.get_all('tag') if tag and tag not in d];
		entry.whereCreated=ENV.CityLatLong;
		entry.whereModified=ENV.CityLatLong;
		entry.put() #save data model object to data base
		#each new create icon should have a makecopy action auto generate right after it is created, so user will see reflection of it right away
		#icons that dont have any makecopy action are likely become garbage (because no one can see or copy it)
		#this can help avoid situtation when icon is created but send makecopy action phase on client is error.
		# write some code here to generate make copy action (need some var from request)
		
		#render
		jsonData=json.dumps( [entry.dictJSON()] )  ;
		
		if callbackJSONP:
			self.response.out.write(callbackJSONP+'('+jsonData+');');
		else: self.response.out.write(jsonData);
		
		return;

class GetIconByID(webapp.RequestHandler):
	def get(self):
		IDs=self.request.get_all('id');
		keyNames=self.request.get_all('keyName');
		callbackJSONP=self.request.get('JSONP');
		entries=[];		
		
		for id in IDs:
			try:
				entry=db.get( db.Key(id));
			except datastore_errors.BadKeyError:	
				continue;
			entries+=[entry];
		
		for keyName in keyNames:
			entry=db.get(db.Key.from_path('Icon',keyName ));
			if entry!=None: entries+=[entry];
		
		jsonData=json.dumps( [entry.dictJSON() for entry in entries]) ;
		if callbackJSONP:
			self.response.out.write(callbackJSONP+'('+jsonData+');');
		else: self.response.out.write(jsonData);
		
class ModifyByID(webapp.RequestHandler):
	def post(self):
		ENV=tool.readHeader(self.request);
		#get icon
		id=self.request.get('id');
		keyName=self.request.get('keyName');
		callbackJSONP=self.request.get('JSONP');
		entry=None;
		if id:
			try:
				entry=db.get( db.Key(id));
			except datastore_errors.BadKeyError:	
				self.response.out.write(json.dumps([]));
				return;
		
		if not entry and keyName:
			entry=db.get(db.Key.from_path('Icon',keyName ));
		
		if entry==None:
			self.response.out.write(json.dumps([]));
			return;
		
		#set new thumb
		thumb = self.request.get('thumb');
		if thumb and len(thumb)>0:entry.thumb=thumb;
		
		#clear tag
		if self.request.get('clearTag'):
			entry.tag=[];
		else:
			#delete tag from icon
			deleteTags = self.request.get_all('dtag');
			for tag in deleteTags:
				try:
					entry.tag.remove(tag);
				except ValueError:	
					continue;
		
		#add more tag to icon		
		tags = self.request.get_all('tag');
		if entry.tag==None:entry.tag=[];
		for tag in tags:
			if tag not in entry.tag:
				entry.tag+=[tag];
		
		#clear content (if clearContent, old content will be wipe out)
		if self.request.get('clearContent'): entry.content={};
		
		#modify value for key by merging content
		try:	
			contentDict=json.loads(entry.content);
			mergeContent=json.loads(self.request.get('mergeContent'));
			contentDict.update(mergeContent);
		except ValueError:
			self.response.out.write(json.dumps([]));	
			return;
		
		#remove none value
#		for key in contentDict:
#			if contentDict[key]==None:
#				del contentDict[key];
				
		entry.content=json.dumps(contentDict);
		entry.whereModified=ENV.CityLatLong;
		entry.put();
		
		jsonData = json.dumps( [entry.dictJSON()]) ;
		
		if callbackJSONP:
			self.response.out.write(callbackJSONP+'('+jsonData+');');
		else: self.response.out.write(jsonData);

		return;
		

#def main():
app = webapp.WSGIApplication([
('/icon/', GetIcon),
('/icon/byid', GetIconByID),
('/icon/modify', ModifyByID),
], debug=True)

#	util.run_wsgi_app(application)
#
#
#if __name__ == '__main__':
#	main()
