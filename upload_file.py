import os
import datetime,json
import urllib


from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from google.appengine.api import datastore_errors;


from google.appengine.api import users
from google.appengine.api import mail

class Custom():
	pass


class MainHandler(webapp.RequestHandler):
	def get(self):
		upload_url = blobstore.create_upload_url('/file/upload')
		self.response.out.write('<html><body>')
		self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
		self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit"
				name="submit" value="Submit"> </form></body></html>""")

class GetUploadLink(webapp.RequestHandler):
	def get(self):
		self.response.out.write( blobstore.create_upload_url('/file/upload') );
		
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		upload_files = self.get_uploads('file')	# 'file' is file upload field in the form
		blob_info = upload_files[0]
		self.response.out.write('/file/serve/%s' % blob_info.key());

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, resource):
		resource = str(urllib.unquote(resource))
		blob_info = blobstore.BlobInfo.get(resource)
		self.send_blob(blob_info)

app = webapp.WSGIApplication(
[('/file/', MainHandler),
('/file/getuploadlink', GetUploadLink),
('/file/upload', UploadHandler),
('/file/serve/([^/]+)?', ServeHandler),
], debug=True)


