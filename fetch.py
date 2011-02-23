#!/usr/bin/env python
# encoding: utf-8
"""
fetch.py

Created by Roy on 2011-02-14.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""    

import re 
import lxml.html
import web
from sinat import Sinat, OAuthToken, OAuthConsumer  
from trunkly import Trunkly
import time

SINA_CONSUMER_KEY = '3892402622' # your App Key
SINA_CONSUMER_SECRET = '6af8bdaa10fb55fa82089a8a29787f81' # your App Secret  

#db = web.database(dbn='mysql', db='roymax_sinaly', user='roymax_sinaly', pw='654no8BAxf8hqnT') 
db = web.database(dbn='mysql', db='SINALY', user='root', pw='')
sinaConsumer = OAuthConsumer(SINA_CONSUMER_KEY, SINA_CONSUMER_SECRET)
p = re.compile('http://[\\w\\.\\-\\/]+')


def main():
	print 'start at %s' % time.asctime()  
	users = db.select("users")
	print 'current users count %s ' % len(users)
	for user in users:
		# print 'user %s ' % user.token
		# print 'user %s ' % user.secret
		access_token = OAuthToken(user.token, user.secret) 
		
		if not user.trunk_key:
			continue
		
		t = Trunkly(user.trunk_key)
		
		sinat = Sinat(sinaConsumer, access_token=access_token)	
		statuses = sinat.statuses__user_timeline('GET')
		for status in statuses:
			weibo = status['text']
			if status.has_key('retweeted_status'):
				weibo = '%s //@%s: %s' % (weibo , 
											status['retweeted_status']['user']['name'],
											status['retweeted_status']['text'])
				
			# print 'status %s' % status['text']
			urls = p.findall(weibo)
			for url in urls:
				print 'url is %s ' % url
				title = None
				trunk = None
				
					
				try:
					html = lxml.html.parse(url)
					title = html.find(".//title").text
					url = html.getroot().base_url
					print 'title is %s' % title 
					print 'base url is %s ' % url
					
					try:
						try:
							trunk = t.get_link(parameters={'url': url})
							print 'url Already exists!!!'
							continue
						except:
							print 'error'
							pass

						if title and not trunk:
							print 'post url to trunk.ly'
							t.post_link(parameters={'url': url,
										'title': title,
										'tags' : '',
										'note' : weibo,
										'text' : weibo})
					except:
						print 'post to trunk error. url %s title %s' % (url, title)
				except:
					print 'url %s fetch error' % (url)
					
	print '---------------- end ---------------------'

if __name__ == '__main__':
	main()

