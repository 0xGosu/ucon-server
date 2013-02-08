from google.appengine.ext import db
from google.appengine.api import users


import re;

class Custom:pass;

def readHeader(request):
	ENV=Custom();
	
	ENV.CurrentUser=users.get_current_user();
	ENV.CityLatLong=None;
	CityLatLong=request.headers.get('X-AppEngine-CityLatLong');
	if CityLatLong: 
		CityLatLong=CityLatLong.split(',');
		ENV.CityLatLong=db.GeoPt(float(CityLatLong[0]),float(CityLatLong[1]));
	
	return ENV;
	