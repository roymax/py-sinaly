#!/usr/bin/env python
# encoding: utf-8
"""
trunkly.py

Created by Roy on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import json 
import httplib2                
from urllib import urlencode
import sys

reload(sys) 
sys.setdefaultencoding("utf-8")

TRUNK_API_HTTP='https://trunkly.com/api/v1'
TRUNK_API_HTTPS='https://trunkly.com/api/v1'
         

HTTP_METHOD = ["GET", "POST", "PUT", "DELETE"]
                                                
class Trunkly:
	"""docstring for Trunkly"""
	def __init__(self, api_key=None):
		self.api_key = api_key 
		
	def get_api_key(self, username=None, password=None):
		method = "GET"
		url = TRUNK_API_HTTPS + '/api_key/'
		
		http = httplib2.Http() 
		http.add_credentials(username,password)
		resp, content = http.request(url, method=method)
       
		if resp['status'] != '200':
			raise Exception("Invalid response %s." % resp['status'])
		return json.loads(content)
		
	
	def cmd(self, args):
		def execute(parameters=None, method="GET"):
			if not parameters:
				parameters = {}
            
			defaults = {'api_key': self.api_key  }
			defaults.update(parameters)
			parameters = defaults
			
			url = TRUNK_API_HTTP
			
			p = False
			for arg in args:
				if arg.upper() in HTTP_METHOD:
					method = arg.upper() 
					# print 'method %s' % method
					continue
				
				if arg != '' and not p:
					url += '/%s' % arg 
				else:
					if p:
						#read parameters
						if arg not in parameters:
							raise Exception("Parameter '%s' is required." % arg)
						url += '/%s' % parameters[arg]
						del parameters[arg]
						p = False
					else:
						p = True
				
			url += '/'
			
			body = None
			param_encoded = urlencode(parameters)
			if method == "POST":
				body = param_encoded
	            # headers['Content-Type'] = 'application/x-www-form-urlencoded'
			elif method == "GET":
				url += '?' + param_encoded
			
			# print 'url is %s ' % url
			# print 'body is %s ' % body
			http = httplib2.Http()
			resp, content = http.request(url, method=method, body=body)

			if resp['status'] != '200':
				raise Exception("Invalid response %s." % resp['status'])
			return json.loads(content) 
			
		return execute
		

	def __getattr__(self, attr):
		# if attr.startswith('_'):
		# 	raise Exception("'Trunkly' object has no attribute '_abc_'")
		# if attr.endswith('_'):
		# 	raise Exception("attr can't end with '_'")
		args = attr.split('_')
		return self.cmd(args)
                  

		
