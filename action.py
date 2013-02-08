import os
import datetime,json
import urllib

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util


from google.appengine.api import users

from google.appengine.api import mail

from database import Action

import tool;

class Custom():
	pass
		

class GetAction(webapp.RequestHandler):
	
	def get(self):
		ENV=tool.readHeader(self.request);
		#Get var from request
		place=self.request.get('place');
		
		matchCurrentUser = self.request.get('createdByMe');
		
		type=self.request.get_all('type')
		
		tags=self.request.get_all('tag');
		
		maxFetch=self.request.get_range('max',0,1000,default=20);
		offset=self.request.get_range('offset',0,10000,default=0);
		
		keys_only=self.request.get('keys_only');
		
		callbackJSONP=self.request.get('JSONP');
		
		#time filter
		#filter > distance time from now
		ddays=self.request.get_range('days',0,365,default=0);
		dhours=self.request.get_range('hours',0,24,default=0);
		dminutes=self.request.get_range('minutes',0,60,default=0);
		if(self.request.get('seconds')):dseconds=abs(int(self.request.get('seconds')));
		else:dseconds=0;
		#filter > timeString1
		timeString1=self.request.get('timeLowerBound');
		
		
		#Query
		if(keys_only):query = db.Query(Action, keys_only=True);
		else:query = db.Query(Action, keys_only=False);
		
		#Filter
		if place:
			query.filter("place =", place);
		if matchCurrentUser:
			query.filter("whoCreated =", ENV.CurrentUser);
		if type:
			query.filter("type IN", type);
		for tag in tags:
			if tag:query.filter("tag =", tag);
		
		if(ddays or dhours or dminutes or dseconds):
			timeFilter=datetime.datetime.now()-datetime.timedelta(days=ddays,hours=dhours,minutes=dminutes,seconds=dseconds );
			query.filter("created >",timeFilter);
		if(timeString1):
			time_lower_bound_filter=datetime.datetime.strptime(timeString1,"%Y-%m-%d %H:%M:%S.%f");
			query.filter("created >",time_lower_bound_filter);
		
		#Sort
		query.order("-created");
		
		#Fetch
		data=[];
		if maxFetch>0:
			data = query.fetch(maxFetch,offset);
		else:
			data = [entry for entry in query];
				
		#reversed, most new at bottom
		entries=reversed(data);
		
		#render
		if(keys_only):
			jsonData = json.dumps( [entry for entry in entries]) ;
		else:
			jsonData = json.dumps( [entry.dictJSON() for entry in entries]) ;
			
		if callbackJSONP:
			self.response.out.write(callbackJSONP+'('+jsonData+');');
		else: self.response.out.write(jsonData);
		
		return;

	def post(self):
		ENV=tool.readHeader(self.request);
		#Get var from request and pass to data model object
		callbackJSONP=self.request.get('JSONP');
		entry = Action()
		try:	
			#check valid json , save as python json
			entry.content=json.dumps( json.loads(self.request.get('content')) );
		except ValueError:
			self.response.out.write(json.dumps([]));	
			return;
		
		#entry.userName = self.request.get('userName');
		entry.place = place = self.request.get('place');
		entry.type = self.request.get('type');
		d={};#temporary dict
		entry.tag = [d.setdefault(tag,tag) for tag in self.request.get_all('tag') if tag and tag not in d];
		entry.whereCreated=ENV.CityLatLong;
		entry.whereModified=ENV.CityLatLong;
		#preprocess before create 
		if self.smartProcessBeforeCreate(entry) : entry.put() #save data model object to data base
		#render
		jsonData = json.dumps( [entry.dictJSON()] )  ;
		
		if callbackJSONP:
			self.response.out.write(callbackJSONP+'('+jsonData+');');
		else: self.response.out.write(jsonData);
		
		
	def smartProcessBeforeCreate(self,action):
		""" 
		(this make first load query with makecopy action better by modify available invole makecopy action)
		Note: action should not be modifed by user intent.
		"""
		content=json.loads(action.content);
		#this should be removed in futute use
		if content.get('iconID'):
			action.iconID=content.get('iconID');
		
		if(action.type=='makecopy'):
			query=db.GqlQuery("Select * from Action where place=:1 and type=:2 and tag=:3"
			,action.place,'makecopy',content.get('iconID'));
			makecopyAction=query.get();
			if makecopyAction:
				if not makecopyAction.tag.get('alive'):
					makecopyAction.tag+=['alive'];
					makecopyAction.put();
				#return False;
				#consider dont save this action on server because there is already a same makecopy action at same place.
			else:
				action.tag+=[content.get('iconID'),'alive'];
			
		if(action.type=='destroy'): #should change type to disable
			query=db.GqlQuery("Select * from Action where place=:1 and type=:2 and tag=:3 and tag=:4"
			,action.place,'makecopy',content.get('iconID'),'alive');
			makecopyAction=query.get();
			if makecopyAction:
				makecopyAction.tag.remove('alive');
				makecopyAction.put();
		
		#this should change to index
		if(action.type=='move'):
			query=db.GqlQuery("Select * from Action where place=:1 and type=:2 and tag=:3 and tag=:4"
			,action.place,'makecopy',content.get('iconID'),'alive');
			makecopyAction=query.get();
			if makecopyAction:
				#merge content of makecopy action with move action
				makecopyActionContent=json.loads(makecopyAction.content);
				makecopyActionContent['index']=content.get('index');
				makecopyAction.content=json.dumps(makecopyActionContent);
				makecopyAction.put();
		
		if(action.type=='checkin'):
			action.tag+=[content.get('iconID'),'available'];
			#consider
			#if there is an available checkin action less than 5 minutes ago, dont save this action
			query=db.GqlQuery("Select * from Action where place=:1 and type=:2 and tag=:3 and tag=:4 and created>:5"
			,action.place,'checkin',content.get('iconID'),'available', datetime.datetime.now()-datetime.timedelta(minutes=5) );
			if query.count(limit=1):return False;
				
		if(action.type=='checkout'):
			query=db.GqlQuery("Select * from Action where place=:1 and type=:2 and tag=:3 and tag=:4 and created>:5"
			,action.place,'checkin',content.get('iconID'),'available', datetime.datetime.now()-datetime.timedelta(minutes=5) );
			#consider: only query for checkin action less than 5 minutes (testing)
			checkinAction = query.get();
			if checkinAction:
				#disable the checkin action that available
				checkinAction.tag.remove('available');
				checkinAction.put();
				
		return True;


#def main():
app = webapp.WSGIApplication([
('/action/', GetAction),
], debug=True)

#	util.run_wsgi_app(application)

#
#if __name__ == '__main__':
#	main()
